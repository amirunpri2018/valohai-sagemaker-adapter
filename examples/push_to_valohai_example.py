import sys
sys.path.append("../../valohai-sagemaker-adapter")

from valohai_sagemaker.valohai import ValohaiAdapter, CodeContainer
from valohai_sagemaker.path import module_rootdir

if __name__ == "__main__":
    adapter = ValohaiAdapter(
        CodeContainer(
            "test-project",
            pip_packages=["imbalanced-learn"],
            files_to_copy=[
                "../examples/jupyter-example/train.py",
                module_rootdir("valohai_sagemaker")
            ]
        ),
        dockerhub_image="ufoym/deepo:pytorch"
    )
    adapter.launch_execution({"training": "some/link/to/data/on/the/internet"})
