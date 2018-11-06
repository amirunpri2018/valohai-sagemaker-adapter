from unittest import TestCase, mock
from valohai_sagemaker import code_container, template
import os


class CodeContainerTest(TestCase):
    NAME = "NAME"
    PATH = "PATH"
    FILES_TO_COPY = ["file1", "file2"]
    PIP_PACKAGES = ["somepackage1", "somepackage2"]
    TRAIN_SCRIPT = "TRAIN_SCRIPT"
    WORKING_DIR = "PWD"
    PYTHON_PATH = "PYTHON_PATH"


    def create_image(self):
        path_delegate = mock.MagicMock()
        path_delegate.join = os.path.join
        path_delegate.basename = os.path.basename
        path_delegate.exists = mock.MagicMock(return_value=True)
        path_delegate.copy = mock.MagicMock()
        path_delegate.remove = mock.MagicMock()
        path_delegate.write_file = mock.MagicMock()

        container = code_container.CodeContainer(name=self.NAME, path=self.PATH,
                                                 files_to_copy=self.FILES_TO_COPY,
                                                 pip_packages=self.PIP_PACKAGES,
                                                 train_script=self.TRAIN_SCRIPT,
                                                 working_dir=self.WORKING_DIR,
                                                 python_path=self.PYTHON_PATH,
                                                 path_delegate=path_delegate)

        return path_delegate, container


    def test_can_instanciate_image(self):
        self.create_image()


    def test_writing_container_directory_raises_if_template_path_does_not_exist(self):
        path_delegate, image = self.create_image()
        path_delegate.exists = mock.MagicMock(return_value=False)

        with self.assertRaises(RuntimeError):
            image.package()


    def test_package_writes_appropriate_template_and_config_files(self):
        path_delegate, image = self.create_image()

        image.package()

        path_delegate.copy.assert_has_calls([
            mock.call(template.container_template_path(), self.PATH),
            mock.call(self.FILES_TO_COPY[0], "PATH/model/user/{}".format(self.FILES_TO_COPY[0])),
            mock.call(self.FILES_TO_COPY[1], "PATH/model/user/{}".format(self.FILES_TO_COPY[1]))
        ])

        path_delegate.write_file.assert_has_calls([
            mock.call("PATH/model/append_python_path.txt", self.PYTHON_PATH),
            mock.call("PATH/model/working_directory.txt", self.WORKING_DIR),
            mock.call("PATH/model/train_script_location.txt", self.TRAIN_SCRIPT)
        ])


    def test_package_remove_previous_container_if_it_exists_already(self):
        path_delegate, image = self.create_image()

        image.package()

        path_delegate.remove.assert_called_with(self.PATH)


    def test_package_doesnt_attempt_to_remove_previous_container_if_it_doesnt_exist(self):
        path_delegate, image = self.create_image()
        def mock_exists(_path):
            if _path == self.PATH:
                return False
            return True
        path_delegate.exists = mock_exists

        image.package()

        path_delegate.remove.assert_not_called()


    def test_copy_files_to_container_copies_files_to_model_path(self):
        path_delegate, image = self.create_image()
        image.write_container_directory = mock.MagicMock()

        image.copy_files_to_container()

        path_delegate.copy.assert_has_calls([
            mock.call(self.FILES_TO_COPY[0], "PATH/model/user/{}".format(self.FILES_TO_COPY[0])),
            mock.call(self.FILES_TO_COPY[1], "PATH/model/user/{}".format(self.FILES_TO_COPY[1]))
        ])


    def test_copy_files_to_container_copies_files_to_model_with_appropriate_path_when_different_than_original(self):
        path_delegate, image = self.create_image()
        image.files_to_copy = ["file1", {"file2": "new_name"}]

        image.copy_files_to_container()

        path_delegate.copy.assert_has_calls([
            mock.call(self.FILES_TO_COPY[0], "PATH/model/user/{}".format(self.FILES_TO_COPY[0])),
            mock.call(self.FILES_TO_COPY[1], "PATH/model/user/{}".format("new_name"))
        ])
