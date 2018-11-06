from .shell import CommandRunner
from .path import PathDelegate
from .template import docker_template_path


class Image(object):
    """
    A class that represents a Docker image to be generated using the template
    provided by the python module, in order to be used with SageMaker.
    Its content is represented by a CodeContainer object.
    """

    def __init__(self, code_container,
                 froms=[], build_commands=[],
                 tag="latest", output_dir=None,
                 path_delegate=None, command_runner=None):
        """
        :param code_container: a CodeContainer object that will represent
                               the docker image content.
        :param froms: list of dependent Docker images on DockerHub.
        :param build_commands: list of strings
                               (commands to run during build in the Dockerfile).
        :param tag: tag for the image to be used, default "latest".
        :param output_dir: output directory to be used for local training and serving,
                           you may leave empty for a
                           default-in-current-working-directory directory to be created.
        :param path_delegate: path handling abstraction class,
                              you most likely don't need to use it.
        :param command_runner: command running abstraction class,
                               you most likely don't need to use it.
        """
        self.code_container = code_container
        self.docker_froms = list(froms)
        self.commands = list(build_commands)
        self.tag = tag
        self.output_dir = output_dir
        self.cmd = command_runner
        self.path_delegate = path_delegate

        if self.path_delegate is None:
            self.path_delegate = PathDelegate()

        if self.output_dir is None:
            self.output_dir = "{}.output".format(self.code_container.name)

        if self.cmd is None:
            self.cmd = CommandRunner()


    @property
    def tagged_name(self):
        """
        :returns: str -- the image + tag in docker format
        """
        return '{}:{}'.format(self.code_container.name, self.tag)


    def dockerfile_content(self):
        """
        Generates on-the-fly the image's Dockerfile using the package's template file
        and the image arguments.

        :raises: RuntimeError
        """
        content = self.path_delegate.\
            read_file_lines(self.path_delegate.join(docker_template_path(),
                                                    "Dockerfile.template"))

        def find_line(lines, condition):
            """nodoc"""
            for idx, line in enumerate(lines):
                if condition(line):
                    return idx
            return None

        from_tag_line = find_line(content, lambda line: "FROM_TAG" in line) + 1

        for i, element in enumerate(self.docker_froms):
            content.insert(from_tag_line + i, "FROM {}\n".format(element))

        pip_tag_line = find_line(content, lambda line: "INSTALL_TAG" in line) + 1

        if len(self.code_container.pip_packages) > 0:
            content.insert(pip_tag_line,
                           "RUN pip3.6 install {} && rm -rf /root/.cache\n"\
                           .format(" ".join(self.code_container.pip_packages)))

        commands_tag_line = find_line(content, lambda line: "COMMANDS_TAG" in line) + 1

        if len(self.commands) > 0:
            content.insert(commands_tag_line,
                           "\n".join(map(lambda line: "RUN {}".format(line),
                                         self.commands)))

        return "".join(content)


    def build(self, verbose=True):
        """
        Generates and builds the Docker image.

        :raises: RuntimeError
        """
        self.code_container.package()
        self.path_delegate.write_file(self.path_delegate.join(self.code_container.path,
                                                              "Dockerfile"),
                                      self.dockerfile_content())

        returncode = self.cmd.run([
            "bash",
            self.path_delegate.join(self.code_container.path, "build.sh"),
            self.code_container.name
        ], verbose=verbose)

        if returncode != 0:
            raise RuntimeError("docker could not build the image: {}".format(self.cmd.stderr))

        self.cmd.reset()


    def push(self, verbose=True, verbose_build=True):
        """
        Pushes the Docker image to ECR. It is required in order to train remotely.
        Push calls automatically the method build, so no need to call build before push.

        :raises: RuntimeError
        """
        self.build(verbose=verbose_build)

        returncode = self.cmd.run([
            "bash",
            self.path_delegate.join(self.code_container.path, "push.sh"),
            self.code_container.name
        ], verbose=verbose)

        if returncode != 0:
            raise RuntimeError("docker could not push the image: {}".format(self.cmd.stderr))

        self.cmd.reset()


    def train(self, verbose=True, verbose_build=False):
        """
        Trains the Docker image "locally" (current machine running the calling program).
        Train calls automatically build, so no need to call build before train.
        No push is involved in local training. Plus this method does not require SageMaker nor AWS.

        :raises: RuntimeError
        """
        self.build(verbose=verbose_build)
        self.path_delegate.create_directory(self.output_dir)

        returncode = self.cmd.run([
            "bash",
            self.path_delegate.join(self.code_container.path, "local_test", "train_local.sh"),
            self.tagged_name,
            self.output_dir
        ], verbose=verbose)

        if returncode != 0:
            raise RuntimeError("training the image failed: {}".format(self.cmd.stderr))

        self.cmd.reset()


    def serve(self, verbose=True, verbose_build=False):
        """
        Experimental, work in progress.
        """
        self.build(verbose=verbose_build)

        returncode = self.cmd.run([
            "bash",
            self.path_delegate.join(self.code_container.path, "local_test", "serve_local.sh"),
            self.tagged_name,

            self.output_dir
        ], verbose=verbose)

        if returncode != 0:
            raise RuntimeError("training the image failed: {}".format(self.cmd.stderr))

        self.cmd.reset()
