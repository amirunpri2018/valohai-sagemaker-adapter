from .path import PathDelegate
from .template import container_template_path


class CodeContainer(object):
    """
    A class that represents a code repository in which a model is going to be trained.
    All of the files you use to train the model must be contained in it.
    """

    def __init__(self, name, path=None,
                 files_to_copy=[], pip_packages=[],
                 train_script="train.py", working_dir="", python_path="",
                 path_delegate=None):
        """
        Instantiate the object's attributes.
        The only required parameter is the :param name:,
        which must be a docker-compatible string for the image to be generated.
        However, for SageMaker to work with a potential model,
        you need to provide a "train.py" file for training the model.

        :param name: name of the code container.
        :param files_to_copy: iterable (of strings or dicts) for the files to copy
                              inside the container.
                              Must contain a "train.py" (or otherwised defined
                              by the train_script param) training file for SageMaker
                              to train your model.
                              Dicts in the iterable must contain only one key-value pair
                              of strings that represents copy argument file names
                              ({from: to}).
        :param pip_packages: list of python pip packages to install while
                             running the container.
        :param train_script: The name of the python script to be run,
                             if train.py does not fit your needs.
        :param working_dir: The working directory in which to run the project
                            inside the container.
        :param python_path: Append the python path
                            (considering the container relative paths) if needed.
        :param path_delegate: path handling abstraction class, you most likely
                              don't need to use it.
        """
        self.name = name

        self.files_to_copy = files_to_copy
        self.pip_packages = list(pip_packages)

        self.train_script = train_script
        self.working_dir = working_dir
        self.python_path = python_path

        self.path = path
        self.path_delegate = path_delegate

        if self.path_delegate is None:
            self.path_delegate = PathDelegate()

        if self.path is None:
            self.path = "{}/{}.container".format(self.path_delegate.current_directory(), self.name)


    def process_files_to_copy(self):
        """nodoc"""
        def process_str_or_dict(element):
            """nodoc"""
            if isinstance(element, str):
                input_filename, output_filename = element, \
                    self.path_delegate.basename(element)
            elif isinstance(element, dict):
                input_filename, output_filename = \
                    list(element.items())[0][0], list(element.items())[0][1]
            else:
                raise TypeError("bad element-in-list argument" +
                                "should be a string(filename) or a " +
                                "dict({filename: copied_filename})")
            return input_filename, output_filename

        if isinstance(self.files_to_copy, list) or isinstance(self.files_to_copy, tuple):
            return list(map(process_str_or_dict, self.files_to_copy))
        else:
            raise TypeError("bad files_to_copy argument, " +
                            "should be either list/tuple of strings(filename) or " +
                            "dicts({filename: copied_filename})")


    def copy_files_to_container(self):
        """nodoc"""
        for input_filename, output_filename in self.process_files_to_copy():
            output_filepath = self.path_delegate.join(self.path, "model", "user", output_filename)
            self.path_delegate.copy(input_filename, output_filepath)


    def write_config_files(self):
        for filename, variable in [["append_python_path.txt", self.python_path],
                                   ["working_directory.txt", self.working_dir],
                                   ["train_script_location.txt", self.train_script]]:
            self.path_delegate.write_file(
                self.path_delegate.join(self.path, "model", filename), variable)


    def package(self):
        """
        Writes the container directory and its content to a .container directory.

        :raises: RuntimeError
        """
        if not self.path_delegate.exists(container_template_path()):
            raise RuntimeError("Package seems to be installed incorrectly, " +
                               "could not find template resource directory: {}"\
                               .format("container_template_path()"))

        if self.path_delegate.exists(self.path):
            self.path_delegate.remove(self.path)
        self.path_delegate.copy(container_template_path(), self.path)
        self.copy_files_to_container()
        self.write_config_files()
