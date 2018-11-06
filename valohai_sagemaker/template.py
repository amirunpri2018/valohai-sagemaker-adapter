import os


def container_template_path():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "container-template")


def docker_template_path():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources", "docker-template")
