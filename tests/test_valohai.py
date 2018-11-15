from unittest import TestCase

from valohai_sagemaker.code_container import CodeContainer
from valohai_sagemaker.valohai import ValohaiAdapter


class ValohaiAdapterTest(TestCase):


    def test_for_smoke(self):
        code_container = CodeContainer(name="mock-name")
        adapter = ValohaiAdapter(code_container)
        self.assertEqual(adapter.code_container, code_container)
