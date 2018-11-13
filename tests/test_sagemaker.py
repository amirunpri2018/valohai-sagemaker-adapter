from unittest import TestCase

from valohai_sagemaker.code_container import CodeContainer
from valohai_sagemaker.docker import Image
from valohai_sagemaker.sagemaker import SageMakerAdapter


class SageMakerAdapterTest(TestCase):


    def test_for_smoke(self):
        image = Image(
            CodeContainer(name="mock-name"),
            froms=["python:3.6"]
        )
        adapter = SageMakerAdapter(image)
        self.assertEqual(adapter.image, image)
