from unittest import TestCase, mock
from valohai_sagemaker import file_transformer as ft


EXT1 = ".ext1"
EXT2 = ".ext2"


class TransformerMock(ft.FileTransformer):


    def __init__(self):
        self.transformed_called = 0
        self.arguments = []


    @property
    def transforming(self):
        return EXT1, EXT2


    def transform(self, _in, _out):
        self.transformed_called += 1
        self.arguments.append((_in, _out))


class TransformerAwarePathDelegateTest(TestCase):
    FILENAME0 = "file0"
    FILENAME1 = "file1{}".format(EXT1)
    FILENAME2 = "file2{}".format(EXT2)


    def test_copy_does_not_transform_if_extension_is_absent_for_both_files(self):
        transformer = TransformerMock()
        path_delegate = ft.TransformationAwarePathDelegate([transformer])
        path_delegate._original_copy = mock.MagicMock()
        path_delegate.remove = mock.MagicMock()

        path_delegate.copy(self.FILENAME0, self.FILENAME0)

        path_delegate._original_copy.assert_has_calls([
            mock.call(self.FILENAME0, self.FILENAME0)
        ])
        path_delegate.remove.assert_not_called()
        self.assertEqual(0, transformer.transformed_called)


    def test_copy_does_not_transform_if_extension_is_absent_for_source_file_only(self):
        transformer = TransformerMock()
        path_delegate = ft.TransformationAwarePathDelegate([transformer])
        path_delegate._original_copy = mock.MagicMock()
        path_delegate.remove = mock.MagicMock()

        path_delegate.copy(self.FILENAME0, self.FILENAME1)

        path_delegate._original_copy.assert_has_calls([
            mock.call(self.FILENAME0, self.FILENAME1)
        ])
        path_delegate.remove.assert_not_called()
        self.assertEqual(0, transformer.transformed_called)


    def test_copy_does_not_transform_if_extension_is_absent_for_destination_file_only(self):
        transformer = TransformerMock()
        path_delegate = ft.TransformationAwarePathDelegate([transformer])
        path_delegate._original_copy = mock.MagicMock()
        path_delegate.remove = mock.MagicMock()

        path_delegate.copy(self.FILENAME1, self.FILENAME0)

        path_delegate._original_copy.assert_has_calls([
            mock.call(self.FILENAME1, self.FILENAME0)
        ])
        path_delegate.remove.assert_not_called()
        self.assertEqual(0, transformer.transformed_called)


    def test_copy_does_not_transform_if_extension_is_identical(self):
        transformer = TransformerMock()
        path_delegate = ft.TransformationAwarePathDelegate([transformer])
        path_delegate._original_copy = mock.MagicMock()
        path_delegate.remove = mock.MagicMock()

        path_delegate.copy(self.FILENAME1, self.FILENAME1)

        path_delegate._original_copy.assert_has_calls([
            mock.call(self.FILENAME1, self.FILENAME1)
        ])
        path_delegate.remove.assert_not_called()
        self.assertEqual(0, transformer.transformed_called)


    def test_copy_does_transform_if_extension_is_different(self):
        transformer = TransformerMock()
        path_delegate = ft.TransformationAwarePathDelegate([transformer])
        path_delegate._original_copy = mock.MagicMock()
        path_delegate.remove = mock.MagicMock()

        path_delegate.copy(self.FILENAME1, self.FILENAME2)

        transformed = "{}.transformed{}".format(self.FILENAME1, EXT2)
        path_delegate._original_copy.assert_has_calls([
            mock.call(transformed, self.FILENAME2)
        ])
        path_delegate.remove.assert_called_with(transformed)
        self.assertEqual(1, transformer.transformed_called)
