import os
import codecs
import json
import yaml
from .path import PathDelegate
from .code_container import CodeContainer
from .shell import CommandRunner
import valohai_cli as vh
import valohai_cli.settings
import valohai_cli.commands
import valohai_cli.commands.project
import valohai_cli.commands.project.link


class ConfigOverride(vh.settings.Settings):
    """
    Valohai CLI configuration override.
    No need to use this class manually.
    It is internally used by ValohaiDelegate.
    """


    def __init__(self, config_filepath):
        """nodoc"""
        super().__init__()
        self.config_filepath = config_filepath


    def get_filename(self):
        """nodoc"""
        return self.config_filepath


class ValohaiDelegate(object):
    """
    Delegate for the Valohai CLI API.
    No need to use this class manually.
    It is internally used by ValohaiAdapter.
    """


    def __init__(self, config_file_path):
        """nodoc"""
        self.config = ConfigOverride(config_file_path)
        self.original_settings = vh.settings.settings


    def link_project(self, project_dir, name):
        """Link the 'project_dir' directory to the Valohai project 'name'."""
        project_dir = os.path.realpath(project_dir)
        try:
            project = vh.commands.project.link.choose_project(project_dir, spec=name)
            if not project:
                raise RuntimeError("no project found from valohai")
            links = vh.settings.settings.get('links', {})
            links[project_dir] = project
            self.config.update({'links': links})
        except vh.commands.project.link.NewProjectInstead:
            if name:
                vh.commands.project.create.create_project(project_dir, name, yes=True)

        self.config.save()


    def find_global_configs(self):
        """Attempts to find the global Valohai configs for the login credentials."""
        try:
            with open(vh.settings.get_settings_file_name("config.json"), "r") as global_config_file:
                return json.load(global_config_file)
        except FileNotFoundError as error:
            raise RuntimeError("The Valohai configuration file " +
                               "was not found on the system. " +
                               "Please login using 'vh login'", error)


    def login(self, host, user, token):
        """Logs the delegate configs in."""
        self.config.data["host"] = host
        self.config.data["user"] = user
        self.config.data["token"] = token


class ValohaiAdapter(object):
    """
    A class that represents a valohai AdHoc project execution.
    This works by passing it a CodeContainer object.
    """


    def __init__(self, code_container,
                 project_name=None,
                 dockerhub_image="python:3.6",
                 cli_args=[],
                 commands=[],
                 path_delegate=None, valohai_delegate=None):
        """
        Instantiate the ValohaiAdapter configuration.

        :param code_container: The CodeContainer object representing
                               the code you want to send to valohai.
        :param project_name: The name of the Valohai project you want to send
                             the container to. (By default it will take the
                             the container's .name).
        :param dockerhub_image: String representing the dockerhub image which
                                Valohai is gonna use as base to run your code in.
        :param cli_args: Additional CLI arguments to give the Valohai CLI API when
                         sending your job to 'execution' command.
        :param commands: Additional CLI commands to run before pip and
                         training execution.
        :param path_delegate: path handling abstraction class,
                              you most likely don't need to use it.
        :param command_runner: command running abstraction class,
                               you most likely don't need to use it.
        """
        self.code_container = code_container
        self.project_name = project_name
        self.dockerhub_image = dockerhub_image
        self.cli_args = list(cli_args)
        self.commands = list(commands)

        self.path_delegate = path_delegate
        self.valohai_delegate = valohai_delegate

        if self.path_delegate is None:
            self.path_delegate = PathDelegate()

        if self.valohai_delegate is None:
            self.valohai_delegate = ValohaiDelegate(self.path_delegate.join(
                code_container.path, "valohai.cfg", "config.json"))


    @property
    def project_path(self):
        """
        path that represents the root of the valohai project pointed
        in the code container.
        """
        return self.path_delegate.realpath(self.path_delegate.join(self.code_container.path, "model"))


    def save_local_configs(self, inputs, parameters):
        """
        Saves the local valohai configs to the code container.
        This step is required by the valohai cli api before launching execution.
        This method is called by lauch_execution. No Need to call it manually.

        :params inputs: a dict of {'directory in valohai inputs to contain the downloaded fie': 'link (https:// or s3://) to download a file'}.
        :params parameters: yaml valohai additional parameters for the job.
        """
        self.path_delegate.create_directory(self.path_delegate.realpath(self.path_delegate.dirname(self.valohai_delegate.config.config_filepath)))

        global_configs = self.valohai_delegate.find_global_configs()

        self.valohai_delegate.login(global_configs["host"],
                                    global_configs["user"],
                                    global_configs["token"])

        project_name = self.project_name if self.project_name is not None else self.code_container.name
        self.valohai_delegate.link_project(self.project_path, project_name)

        step = {"step": {
            "name": "execution",
            "image": self.dockerhub_image,
            "command": "{pip}{cmd}bash ./train".format(
                pip = ("pip3 install {} && ".format(" ".join(self.code_container.pip_packages)) if len(self.code_container.pip_packages) > 0 else ""),
                cmd = ("{} && ".format(" && ".join(self.commands)) if len(self.commands) > 0 else "")
            )
        }}

        if len(inputs) > 0:
            step["step"].update({
                "inputs": [{"name": name, "default": link} for name, link in inputs.items()]
            })

        if len(parameters) > 0:
            step["step"].update({"parameters": parameters})

        self.path_delegate.write_file(
            self.path_delegate.join(self.project_path, "valohai.yaml"),
            yaml.dump([step])
        )


    def launch_execution(self, inputs={}, parameters={}):
        """
        Attempts to package the code container, push it to the Valohai project,
        and launch the execution on the remote server.

        :params inputs: a dict of {'directory in valohai inputs to contain the downloaded fie': 'link (https:// or s3://) to download a file'}.
        :params parameters: yaml valohai additional parameters for the job.
        """
        self.code_container.package()
        self.save_local_configs(inputs, parameters)

        env = os.environ.copy()
        env.update({"VALOHAI_CONFIG_DIR": self.path_delegate.realpath(self.path_delegate.dirname(self.valohai_delegate.config.config_filepath))})

        CommandRunner().run(["vh", "execution", "run", "--adhoc", "execution"] + self.cli_args,
                            popen_kwargs={"env": env, "cwd": self.project_path})
