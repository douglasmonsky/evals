import ast
from typing import Any, List, Union
from transformers import StringTransformer
from python_code import PythonCode


class PythonCompressor:

    def __init__(self, object_: Any, transformers: List[Union[ast.NodeTransformer, StringTransformer]]) -> None:
        self.code = PythonCode(object_)
        self.transformers = transformers

    def compress(self) -> str:
        for transformer in self.transformers:
            self.code.transform(transformer)
        return self.code

    def retrieve_code(self) -> str:
        return self.code.raw_code


if __name__ == '__main__':
    code = PythonCompressor(PythonCode, [])
    print(code.compress())
    print(code.retrieve_code())