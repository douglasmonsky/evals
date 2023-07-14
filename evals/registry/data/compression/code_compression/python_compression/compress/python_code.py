import ast
import inspect
from typing import Any, Union
from transformers import StringTransformer


class PythonCode:

    def __init__(self, object_: Any) -> None:
        self.object = object_
        self.raw_code = self._retrieve()
        self.ast = ast.parse(self.raw_code)

    def visit(self, visitor: ast.NodeVisitor) -> None:
        """Visit the code with the given visitor."""
        return visitor.visit(self.ast)

    def transform(self, transformer: Union[ast.NodeTransformer, StringTransformer]) -> None:
        """Transform the code with the given transformer."""
        if isinstance(transformer, ast.NodeTransformer):
            self.ast = transformer.visit(self.ast)
            # Update raw code to match transformed AST (Python 3.9+)
            self.raw_code = ast.unparse(self.ast)
        else:
            # Assume the transformer is a text transformer function
            self.raw_code = transformer.visit(self.raw_code)
            # Update AST to match transformed raw code
            self.ast = ast.parse(self.raw_code)

    def _retrieve(self) -> str:
        inspection = inspect.getsource(self.object)
        return inspection

    @property
    def type(self) -> Any:
        return type(self.object)

    def __len__(self) -> int:
        """returns how many lines of code are in the object"""
        return len(self.raw_code.splitlines())

    def __str__(self) -> str:
        return self.raw_code

    def __repr__(self) -> str:
        return f"PythonCode({self.object})"


if __name__ == '__main__':
    code = PythonCode(PythonCode)
    print(code)
    print(code.ast)
