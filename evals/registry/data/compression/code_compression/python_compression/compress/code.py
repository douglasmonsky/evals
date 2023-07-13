import ast
import inspect
from typing import Any


class PythonCode:

    def __init__(self, object_: Any) -> None:
        self.object = object_
        self.raw_code = self._retrieve()

    def visit(self, visitor: Any) -> None:
        """Visit the code with the given visitor."""
        visitor.visit(self)

    def _retrieve(self) -> str:
        inspection = inspect.getsource(self.object)
        return inspection

    @property
    def type(self) -> Any:
        return type(self.object)

    @property
    def ast(self) -> ast.AST:
        return ast.parse(self.raw_code)

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
