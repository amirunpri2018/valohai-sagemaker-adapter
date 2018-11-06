from abc import abstractproperty, abstractmethod
from .path import PathDelegate


class FileTransformer(object):
    @abstractproperty
    def transforming(self):
        pass


    @abstractmethod
    def transform(self, input_filename, output_filename):
        pass


class FileTransformerContainer(object):
    def __init__(self):
        self.transformers = {}


    def __getitem__(self, exts):
        ext1, ext2 = exts
        return self.transformers["{}=>{}".format(ext1, ext2)]


    def __setitem__(self, exts, transformer):
        ext1, ext2 = exts
        self.transformers["{}=>{}".format(ext1, ext2)] = transformer


class TransformationAwarePathDelegate(PathDelegate):
    def __init__(self, file_transformers=[]):
        super().__init__()
        self.transformers = FileTransformerContainer()

        for file_transformer in file_transformers:
            self.register_file_transformer(file_transformer)


    def register_file_transformer(self, transformer):
        ext1, ext2 = transformer.transforming
        self.transformers[ext1, ext2] = transformer


    def _original_copy(self, source, destination):
        return super().copy(source, destination)


    def copy(self, source, destination):
        ext1 = self.file_extension(source)
        ext2 = self.file_extension(destination)

        if ext1 != ext2 and ext1 != '' and ext2 != '':
            transformed = source + ".transformed" + ext2
            self.transformers[ext1, ext2].transform(source, transformed)
            self._original_copy(transformed, destination)
            self.remove(transformed)
        else:
            self._original_copy(source, destination)
