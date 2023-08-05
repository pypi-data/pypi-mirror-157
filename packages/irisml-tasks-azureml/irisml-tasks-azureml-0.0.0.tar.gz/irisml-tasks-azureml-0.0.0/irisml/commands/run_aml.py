import argparse
import contextlib
import json
import os
import pathlib
import shutil
import tempfile
import typing
import azureml.core
import pkg_resources
from irisml.core import JobDescription


class AMLJobManager:
    def __init__(self, subscription_id, workspace_name, experiment_name, compute_target_name):
        self._workspace = self._get_workspace(subscription_id, workspace_name)
        self._experiment = azureml.core.Experiment(workspace=self._workspace, name=experiment_name)
        self._compute_target_name = compute_target_name

    def _get_workspace(self, subscription_id, workspace_name):
        ws_dict = azureml.core.Workspace.list(subscription_id=subscription_id)
        workspaces = ws_dict.get(workspace_name)
        if not workspaces:
            raise RuntimeError(f"Workspace {workspace_name} is not found.")
        if len(workspaces) >= 2:
            raise RuntimeError("Multiple workspaces are found.")

        return workspaces[0]

    def _get_environment(self, job_env):
        env = azureml.core.environment.Environment(name='irisml')
        conda_dep = azureml.core.conda_dependencies.CondaDependencies()
        for package in job_env.pip_packages:
            conda_dep.add_pip_package(package)
        env.python.conda_dependencies = conda_dep
        return env

    def _get_compute_target(self):
        if self._compute_target_name == 'local':
            return 'local'
        return azureml.core.compute.ComputeTarget(workspace=self._workspace, name=self._compute_target_name)

    def submit(self, job, job_env):
        with job.create_project_directory() as project_dir:
            script_run_config = azureml.core.ScriptRunConfig(source_directory=project_dir, compute_target=self._get_compute_target(), environment=self._get_environment(job_env), command=job.command)
            run = self._experiment.submit(config=script_run_config)
            return AzureMLRun(run)


class Job:
    def __init__(self, job_description_filepath: pathlib.Path, environment_variables):
        # Check if the given file is a valid JobDescription
        job_description_dict = json.loads(job_description_filepath.read_text())
        job_description = JobDescription.from_dict(job_description_dict)
        if job_description is None:
            raise RuntimeError(f"The given file is not a valid job description: {job_description_filepath}")

        self._job_description_filepath = job_description_filepath
        self._environment_variables = environment_variables
        self._custom_task_relative_paths = []

    @property
    def name(self):
        return self._job_description_filepath.name

    @property
    def command(self):
        c = f'irisml_run {self.name} -v'
        if self._custom_task_relative_paths:  # Add the current directory to PYTHONPATH so that the custom tasks can be loaded.
            c = 'PYTHONPATH=.:$PYTHONPATH ' + c
        return c

    def add_custom_tasks(self, tasks_dir: pathlib.Path):
        self._custom_task_relative_paths = [str(p.relative_to(tasks_dir)) for p in tasks_dir.rglob('*.py')]
        self._custom_task_dir = tasks_dir

    @contextlib.contextmanager
    def create_project_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir = pathlib.Path(temp_dir)
            shutil.copy(self._job_description_filepath, temp_dir)
            for p in self._custom_task_relative_paths:
                if p.startswith('irisml/tasks'):
                    dest = temp_dir / p
                else:
                    dest = temp_dir / 'irisml' / 'tasks' / p

                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(self._custom_task_dir / p, dest)
            yield temp_dir


class JobEnvironment:
    STANDARD_PACKAGES = ['irisml', 'irisml-tasks', 'irisml-tasks-training']

    def __init__(self, base_docker_image, base_docker_image_registry, custom_packages, extra_index_url=None):
        self._base_docker_image = base_docker_image
        self._base_docker_image_registry = base_docker_image_registry
        self._custom_packages = custom_packages
        self._extra_index_url = extra_index_url
        self._standard_packages = self._find_standard_packages()

    @property
    def base_docker_image(self):
        return self._base_docker_image and (self._base_docker_image, self._base_docker_image_registry)

    @property
    def pip_packages(self):
        return self._standard_packages + self._custom_packages

    @property
    def extra_index_url(self):
        return self._extra_index_url

    def _find_standard_packages(self) -> typing.Tuple[str, str]:
        return sorted([w.project_name + '==' + w.version for w in pkg_resources.working_set if w.project_name in self.STANDARD_PACKAGES])

    def __str__(self):
        s = ''
        if self._base_docker_image:
            s += f'Base Docker: {self._base_docker_image}'
            if self._base_docker_image_registry:
                s += f' ({self._base_docker_image_registry})'
            s += '\n'
        s += f'Packages: {",".join(self.pip_packages)}'
        if self.extra_index_url:
            s += f'\nExtra index url: {self.extra_index_url}'
        return s


class AzureMLRun:
    def __init__(self, run):
        self._run = run

    def wait_for_completion(self):
        return self._run.wait_for_completion(show_output=True)

    def __str__(self):
        return f'AzureML Run(id={self._run.id}, url={self._run.get_portal_url()}'


def main():
    class KeyValuePairAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            k, v = values.split('=', 1)
            d = getattr(namespace, self.dest)
            d[k] = v

    parser = argparse.ArgumentParser()
    parser.add_argument('job_filepath', type=pathlib.Path)
    parser.add_argument('--env', '-e', nargs=1, default={}, action=KeyValuePairAction)
    parser.add_argument('--cache_url', default=os.getenv('IRISML_CACHE_URL'))
    parser.add_argument('--no_cache', action='store_true')
    parser.add_argument('--include_local_tasks', '-l', nargs='?', const=pathlib.Path(), default=None, type=pathlib.Path)
    parser.add_argument('--custom_packages', '-p', nargs='+', default=[])
    parser.add_argument('--extra_index_url')
    parser.add_argument('--no_wait', action='store_true')
    parser.add_argument('--compute_target', default=os.getenv('IRISML_AML_COMPUTE_TARGET'))
    parser.add_argument('--subscription_id', default=os.getenv('IRISML_AML_SUBSCRIPTION_ID'))
    parser.add_argument('--workspace', default=os.getenv('IRISML_AML_WORKSPACE_NAME'))
    parser.add_argument('--experiment', default=os.getenv('IRISML_AML_EXPERIMENT_NAME', 'irisml'))
    parser.add_argument('--base_docker_image')
    parser.add_argument('--base_docker_image_registry')

    args = parser.parse_args()

    envs = args.env
    if args.cache_url and not args.no_cache:
        envs['IRISML_CACHE_URL'] = args.cache_url

    job = Job(args.job_filepath, envs)
    if args.include_local_tasks:
        job.add_custom_tasks(args.include_local_tasks)

    env = JobEnvironment(args.base_docker_image, args.base_docker_image_registry, args.custom_packages, args.extra_index_url)
    print(env)

    job_manager = AMLJobManager(args.subscription_id, args.workspace, args.experiment, args.compute_target)
    run = job_manager.submit(job, env)
    print(run)

    if not args.no_wait:
        run.wait_for_completion()
