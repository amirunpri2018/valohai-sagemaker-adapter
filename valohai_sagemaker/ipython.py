import json
from functools import reduce
from itertools import starmap
import os
from .path import PathDelegate
from .code_container import CodeContainer
from .file_transformer import FileTransformer, TransformationAwarePathDelegate


BEGIN_TAG = "##BEGIN##"
END_TAG = "##END##"


class IPythonNotebookFileTransformer(FileTransformer):
    """
    Transforms any given IPython file (.ipynb) to normal python script (.py).
    It works by finding the tags defined by BEGIN_TAG and END_TAG in the cell's code.
    Any in-between-tags code will be copied to the resulting script, all over the
    input notebook. No matter how many in-between-tags blocks there are.
    """


    def __init__(self, path_delegate=None):
        self.path_delegate = path_delegate

        if self.path_delegate is None:
            self.path_delegate = PathDelegate()


    @property
    def transforming(self):
        return ".ipynb", ".py"


    def get_tagged_code(self, filename):
        content = json.loads(self.path_delegate.read_file(filename))

        code_cells = filter(lambda x: x["cell_type"] == "code", content["cells"])
        all_code_lines = reduce(lambda x, y: x + y, map(lambda x: x["source"], code_cells))
        cleaned_code_lines = tuple(map(lambda line: line if line[-1] == "\n" else line + "\n",
                                       all_code_lines))

        begin_tag_line_indices = map(lambda pair: pair[0], filter(lambda pair: BEGIN_TAG in pair[1],
                                                              enumerate(cleaned_code_lines)))
        end_tag_line_indices = map(lambda pair: pair[0], filter(lambda pair: END_TAG in pair[1],
                                                            enumerate(cleaned_code_lines)))
        tagged_line_blocks = starmap(lambda begin, end: cleaned_code_lines[begin+1:end],
                                         zip(begin_tag_line_indices, end_tag_line_indices))

        all_blocks = reduce(lambda x, y: x + y, tagged_line_blocks)

        return "".join(all_blocks)


    def transform(self, input_filename, output_filename):
        if self.path_delegate.file_extension(input_filename) == ".ipynb":
            self.path_delegate.write_file(output_filename, self.get_tagged_code(input_filename))


def create_ipython_code_container(name, **kwargs):
    """
    Creates a CodeContainer object that transforms any .ipynb file mapped to a .py file to a .py file in the container.
    """
    return CodeContainer(name, **kwargs,
                         path_delegate=TransformationAwarePathDelegate(file_transformers=[
                             IPythonNotebookFileTransformer()
                         ]))
