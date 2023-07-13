import ast
from python_compression.compress import IdentifierRenamingTransformer
from typing import Tuple


def rename_identifiers(source_code: str, rename_self:bool = False) -> Tuple[str, ast.AST]:
    """Helper function to rename identifiers in the source code"""
    tree = ast.parse(source_code)
    renamer = IdentifierRenamingTransformer(rename_self=rename_self)
    new_tree = renamer.visit(tree)
    new_code = ast.unparse(new_tree)
    return new_code.strip(), new_tree


def test_function_name_renaming() -> None:
    source_code = """
def foo(a, b):
    return a + b
"""
    _, tree = rename_identifiers(source_code)
    function_def = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)][0]
    assert function_def.name == 'a'


def test_function_variable_name_renaming() -> None:
    source_code = """
def foo(a, b):
    return a + b
"""
    _, tree = rename_identifiers(source_code)
    function_def = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)][0]
    arg_names = [arg.arg for arg in function_def.args.args]
    assert arg_names == ['b', 'c']


def test_class_name_renaming() -> None:
    source_code = """
class Foo:
    def bar(self, a, b):
        return a + b
"""
    _, tree = rename_identifiers(source_code)
    class_def = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)][0]
    assert class_def.name == 'A'


def test_method_name_renaming() -> None:
    source_code = """
class Foo:
    def bar(self, a, b):
        return a + b
"""
    _, tree = rename_identifiers(source_code)
    function_def = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)][0]
    assert function_def.name == 'a'


def test_self_not_renamed() -> None:
    source_code = """
class Foo:
    def bar(self, a, b):
        self.c = a + b
        return self.c
"""
    _, tree = rename_identifiers(source_code)
    attribute = [node for node in ast.walk(tree) if isinstance(node, ast.Attribute)][0]
    assert attribute.value.id == 'self'


def test_self_renamed() -> None:
    source_code = """
class Foo:
    def bar(self, a, b):
        self.c = a + b
        return self.c
"""
    _, tree = rename_identifiers(source_code, rename_self=True)
    attribute = [node for node in ast.walk(tree) if isinstance(node, ast.Attribute)][0]
    assert attribute.value.id != 'self'
