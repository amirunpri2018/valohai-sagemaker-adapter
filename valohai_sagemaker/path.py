import os
import shutil
import importlib


class PathDelegate(object):
    def exists(self, path):
        return os.path.exists(path)


    def read_file(self, path, mode="r"):
        with open(path, mode) as file:
            return file.read()


    def read_file_lines(self, path, mode="r"):
        with open(path, mode) as file:
            return file.readlines()


    def write_file(self, path, content, mode="w"):
        with open(path, mode) as file:
            file.write(content)


    def create_directory(self, path):
        if not os.path.exists(path):
            os.mkdir(path)


    def join(self, *args):
        return os.path.join(*args)


    def current_directory(self):
        return os.curdir


    def copy(self, source, destination):
        try:
            shutil.copytree(source, destination)
        except NotADirectoryError:
            shutil.copy2(source, destination)


    def file_extension(self, filename):
        return os.path.splitext(filename)[1]


    def dirname(self, filename):
        return os.path.dirname(filename)


    def basename(self, filename):
        return os.path.basename(filename)


    def basename_no_extension(self, filename):
        return os.path.splitext(filename)[0]


    def realpath(self, filename):
        return os.path.realpath(filename)


    def remove(self, filename):
        try:
            shutil.rmtree(filename)
        except NotADirectoryError:
            os.remove(filename)


def module_rootdir(module_name):
    """
    Returns the absolute path of the installation location of a module.
    Useful if you want to install a directory of source code in a container
    without necessarily having it packaged in a python egg.

    For e.g.:
    module_rootdir("os") == "/home/ec2-user/anaconda3/envs/python3/lib/python3.6/"
    module_rootdir("some_module_in_the_same_dir_as_my_notebook_running") == "path/to/dir/of/my/notebook"
    """
    module = importlib.import_module(module_name)
    return os.path.dirname(module.__file__)
