from unittest import TestCase, mock
from valohai_sagemaker import docker
import os


class ImageTest(TestCase):
    NAME = "NAME"
    FILES_TO_COPY = ["file1", "file2"]
    PATH = "PATH"
    TAG = "TAG"
    DOCKER_FROMS = ["image1", "image2"]
    PIP_PACKAGES = ["somepackage1", "somepackage2"]
    COMMANDS = ["somecommand1", "somecommand2"]
    OUTPUT_DIR = "OUTPUT_DIR"


    def create_image(self):
        cmd_runner = mock.MagicMock()
        cmd_runner.run = mock.MagicMock(return_value=0)
        cmd_runner.reset = mock.MagicMock()

        path_delegate = mock.MagicMock()
        path_delegate.join = os.path.join
        path_delegate.basename = os.path.basename
        path_delegate.exists = mock.MagicMock(return_value=True)
        path_delegate.copy = mock.MagicMock()
        path_delegate.remove = mock.MagicMock()
        path_delegate.write_file = mock.MagicMock()
        path_delegate.create_directory = mock.MagicMock()

        container = mock.MagicMock()
        container.name = self.NAME
        container.path = self.PATH
        container.pip_packages = self.PIP_PACKAGES
        container.package = mock.MagicMock()
        container.copy_files_to_container = mock.MagicMock()

        image = docker.Image(container,
                             froms=self.DOCKER_FROMS, build_commands=self.COMMANDS,
                             tag=self.TAG, output_dir=self.OUTPUT_DIR,
                             path_delegate=path_delegate, command_runner=cmd_runner)

        return container, cmd_runner, path_delegate, image


    def test_can_instanciate_image(self):
        self.create_image()


    def test_tagged_name_is_appropriate(self):
        _, _, _, image = self.create_image()

        self.assertEqual("{}:{}".format(self.NAME, self.TAG), image.tagged_name)


    def test_dockerfile_content_produces_required_input_dependencies(self):
        _, _, path_delegate, image = self.create_image()
        path_delegate.read_file_lines = mock.MagicMock(return_value=[
            "## FROM_TAG ##",
            "## INSTALL_TAG ##",
            "## COMMANDS_TAG ##"
        ])

        content = image.dockerfile_content()

        for docker_from in self.DOCKER_FROMS:
            self.assertIn("FROM {}".format(docker_from), content)

        self.assertIn("install {}".format(" ".join(self.PIP_PACKAGES)), content)

        for command in self.COMMANDS:
            self.assertIn("RUN {}".format(command), content)


    def test_build_calls_package_on_container(self):
        container, _, _, image = self.create_image()
        image.dockerfile_content = mock.MagicMock(return_value="APPROPRIATE_CONTENT")

        image.build()

        container.package.assert_called()


    def test_build_writes_dockerfile_content_with_appropriate_content_at_appropriate_path(self):
        _, _, path_delegate, image = self.create_image()
        image.dockerfile_content = mock.MagicMock(return_value="APPROPRIATE_CONTENT")

        image.build()

        path_delegate.write_file.asser_called_with("{}/{}".format(self.PATH, "Dockerfile"), "APPROPRIATE_CONTENT")


    def test_build_calls_the_build_script_with_appropriate_content_with_appropriate_path(self):
        _, cmd_runner, path_delegate, image = self.create_image()
        image.dockerfile_content = mock.MagicMock()

        image.build(verbose=True)

        cmd_runner.run.asser_called_with([
            "bash", "{}/{}".format(self.PATH, "build.sh"), self.NAME
        ], verbose=True)


    def test_build_calls_reset_on_command_runner_after_successful_build(self):
        _, cmd_runner, _, image = self.create_image()
        image.dockerfile_content = mock.MagicMock()

        image.build()

        cmd_runner.reset.assert_called()


    def test_build_raises_when_build_script_call_fails(self):
        _, cmd_runner, _, image = self.create_image()
        image.dockerfile_content = mock.MagicMock()
        cmd_runner.run = mock.MagicMock(return_value=1)

        with self.assertRaises(RuntimeError):
            image.build()


    def test_build_does_not_call_reset_on_command_runner_after_unsuccessful_build(self):
        _, cmd_runner, _, image = self.create_image()
        image.dockerfile_content = mock.MagicMock()
        cmd_runner.run = mock.MagicMock(return_value=1)

        with self.assertRaises(RuntimeError):
            image.build()

        cmd_runner.reset.assert_not_called()


    def test_push_calls_build_first(self):
        _, _, _, image = self.create_image()
        image.build = mock.MagicMock()
        mock_boolean = mock.MagicMock()

        image.push(verbose_build=mock_boolean)

        image.build.asser_called_with(verbose=mock_boolean)


    def test_push_calls_push_script_with_appropriate_arguments(self):
        _, cmd_runner, _, image = self.create_image()
        image.build = mock.MagicMock()

        image.push()

        cmd_runner.run.assert_called_with([
            "bash", "{}/{}".format(self.PATH, "push.sh"), self.NAME
        ], verbose=True)


    def test_push_raises_when_push_script_call_fails(self):
        _, cmd_runner, _, image = self.create_image()
        image.build = mock.MagicMock()
        cmd_runner.run = mock.MagicMock(return_value=1)

        with self.assertRaises(RuntimeError):
            image.push()


    def test_push_does_not_call_command_runner_reset_when_push_script_call_fails(self):
        _, cmd_runner, _, image = self.create_image()
        image.build = mock.MagicMock()
        cmd_runner.run = mock.MagicMock(return_value=1)

        with self.assertRaises(RuntimeError):
            image.push()

        cmd_runner.reset.assert_not_called()


    def test_push_calls_command_runner_reset_when_push_script_call_is_successful(self):
        _, cmd_runner, _, image = self.create_image()
        image.build = mock.MagicMock()
        cmd_runner.run = mock.MagicMock(return_value=0)

        image.push()

        cmd_runner.reset.assert_called()


    def test_train_calls_build_first(self):
        _, _, _, image = self.create_image()
        image.build = mock.MagicMock()
        mock_boolean = mock.MagicMock()

        image.train(verbose_build=mock_boolean)

        image.build.assert_called_with(verbose=mock_boolean)


    def test_train_creates_directory_for_output_files(self):
        _, cmd_runner, path_delegate, image = self.create_image()
        image.build = mock.MagicMock()

        image.train()

        path_delegate.create_directory.assert_called_with(self.OUTPUT_DIR)


    def test_train_calls_train_script_with_appropriate_arguments(self):
        _, cmd_runner, _, image = self.create_image()
        image.build = mock.MagicMock()

        image.train()

        cmd_runner.run.assert_called_with([
            "bash",
            "{}/{}/{}".format(self.PATH, "local_test", "train_local.sh"),
            "{}:{}".format(self.NAME, self.TAG),
            self.OUTPUT_DIR
        ], verbose=True)


    def test_train_calls_reset_when_successful_build(self):
        _, cmd_runner, _, image = self.create_image()
        image.build = mock.MagicMock()
        cmd_runner.run = mock.MagicMock(return_value=0)

        image.train()

        cmd_runner.reset.assert_called()


    def test_train_raises_when_unsuccessful_build(self):
        _, cmd_runner, _, image = self.create_image()
        image.build = mock.MagicMock()
        cmd_runner.run = mock.MagicMock(return_value=1)

        with self.assertRaises(RuntimeError):
            image.train()


    def test_train_does_not_call_reset_when_unsuccessful_build(self):
        _, cmd_runner, _, image = self.create_image()
        image.build = mock.MagicMock()
        cmd_runner.run = mock.MagicMock(return_value=1)

        with self.assertRaises(RuntimeError):
            image.train()

        cmd_runner.reset.assert_not_called()
