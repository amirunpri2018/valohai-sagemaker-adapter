from setuptools import setup, find_packages

with open('LICENSE') as f:
    license = f.read()

setup(
    name="valohai-sagemaker-adapter",
    version="0.0.1",
    description="Valohai adapter and automatic Docker image generator and runner for Amazon AWS SageMaker.",
    author="Jonathan Gingras",
    author_email="jonathan.gingras.1@gmail.com",
    license=license,
    packages=find_packages(exclude=('docs', 'tests', 'tests.*')),
    package_data={
        'valohai_sagemaker.resources': [
            'container-template/*',
            'container-template/local_test/*',
            'container-template/model/*',
            'container-template/model/user/*',
            'docker-template/*'
        ]
    },
)
