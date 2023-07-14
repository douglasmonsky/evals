import ast
import string
import itertools
from abc import ABC, abstractmethod
from typing import List, Optional, Generator


class StringTransformer(ABC):
    """
    Abstract base class for string transformers.
    Derived classes need to implement the `visit` method.
    """

    @abstractmethod
    def visit(self, raw_code: str) -> str:
        """
        Abstract method to process and transform a given string.

        This method should be implemented by any class that inherits
        from `StringTransformer`. The implementation should take a
        string, perform some transformation on it, and return the
        transformed string.

        :param raw_code: String to be transformed.
        :return: Transformed string.
        """
        pass


class IndentationStringTransformer(StringTransformer):
    """A transformer class to modify string indentation."""

    def __init__(self, new_indent: int = 4) -> None:
        self.new_indent = new_indent

    def visit(self, raw_code: str) -> str:
        """Transform string with new indents."""

        # Split the code into lines
        lines = raw_code.split("\n")

        # Determine the original number of indentation spaces
        indentation_spaces = self.determine_indentation(raw_code)

        # Process each line to modify its indentation
        for i, line in enumerate(lines):
            # Count the leading spaces
            leading_space_count = len(line) - len(line.lstrip(' '))

            # Calculate the new indentation level
            indent_level = leading_space_count // indentation_spaces

            # Generate the new leading spaces
            new_leading_spaces = ' ' * (self.new_indent * indent_level)

            # Replace each line with new indentation
            lines[i] = f"{new_leading_spaces}{line.lstrip()}"

        # Join the lines back together
        return "\n".join(lines)

    @staticmethod
    def determine_indentation(raw_code: str) -> int:
        """Determines the number of spaces used for indentation in the given code."""

        # Ignore lines that are empty or only contain whitespace
        lines = (line for line in raw_code.split("\n") if line.strip())

        # Calculate the leading spaces for each non-empty line
        leading_spaces_counts = (len(line) - len(line.lstrip(' ')) for line in lines)

        # Filter out counts of zero
        non_zero_counts = (count for count in leading_spaces_counts if count > 0)

        # Return the smallest count (i.e., the current indentation size)
        return min(non_zero_counts, default=0)


class RemoveEmptyLinesTransformer(StringTransformer):
    """A transformer class to remove empty lines from a string."""

    def visit(self, raw_code: str) -> str:
        """Transform string by removing empty lines."""
        # Split the code into lines
        lines = raw_code.split("\n")

        # Filter out empty lines
        non_empty_lines = (line for line in lines if line.strip())
        return "\n".join(non_empty_lines)


class RemoveDocstringsTransformer(ast.NodeTransformer):
    """
    A transformer that removes docstrings from the AST.
    """
    def __init__(self) -> None:
        """Initialize the transformer, setting up dictionary to store the docstrings."""
        self.docstrings = {}

    def handle_docstring(self, node: ast.AST) -> None:
        """
        Handles potential docstrings in the given node by removing them and storing them in a dictionary.

        :param node: The node (function, class, or module) to handle.
        """
        # Get the first statement in the body of the node.
        first_stmt = node.body[0] if node.body else None

        # Check if the first statement is an expression containing a string or a constant.
        # If it is, we consider it to be a docstring.
        if isinstance(first_stmt, ast.Expr) and isinstance(first_stmt.value, (ast.Str, ast.Constant)):
            # Extract the docstring from the expression.
            docstring_expr = first_stmt.value
            docstring = docstring_expr.s if isinstance(docstring_expr, ast.Str) else docstring_expr.value

            # Get the name of the node. If the node doesn't have a name (for example, if it's a module),
            # we use the string 'module' as its name.
            node_name = getattr(node, 'name', 'module')

            # Store the removed docstring in our dictionary, keyed by the name of the node.
            self.docstrings[node_name] = docstring

            # Remove the docstring from the body of the node.
            node.body = node.body[1:]

    def visit(self, node: ast.AST) -> ast.AST:
        """
        Visit an AST node and potentially remove a docstring.

        :param node: The node to visit.
        :return: The visited node.
        """
        # If the node is a function definition, a class definition, or a module, we handle the docstring.
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            self.handle_docstring(node)

        # Continue the traversal as normal for all nodes.
        return self.generic_visit(node)

    def clear_docstrings(self) -> None:
        """Clear the docstrings dictionary."""
        self.docstrings = {}


class IdentifierRenamingTransformer(ast.NodeTransformer):
    """
    Class to transform identifiers in the AST.
    """
    # TODO(Monsky): Bugfix - class methods that are called elsewhere in the class are not properly renamed.
    # Name of the single character redefinition of the method. Need to implement a helper class that encapsulates the
    # renaming of methods and variables attaching them to the class they belong to.
    def __init__(self, rename_self: bool = False) -> None:
        """Initialize transformer, setting up name generators and maps and deciding whether to rename 'self'."""
        self.new_names = self.generate_names(string.ascii_lowercase)
        self.new_class_names = self.generate_names(string.ascii_uppercase)
        self.names_map = [{}]
        self.rename_self = rename_self

    @staticmethod
    def generate_names(alphabet: str) -> Generator[str, None, None]:
        """
        Generate new names from a given alphabet.

        The generation starts from single-letter names, then moves on to
        two-letter names, and so on, exploring all possible combinations
        of the given alphabet.
        """
        for size in itertools.count(1):
            for s in itertools.product(alphabet, repeat=size):
                yield "".join(s)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Transform function definition nodes."""
        self.names_map.append({})
        old_name = node.name
        new_name = next(self.new_names)
        node.name = new_name
        self.names_map[-1][old_name] = new_name

        # Rename function arguments
        for arg in node.args.args:
            if arg.arg == 'self' and not self.rename_self:
                continue
            old_arg_name = arg.arg
            new_arg_name = next(self.new_names)
            self.names_map[-1][old_arg_name] = new_arg_name
            arg.arg = new_arg_name

        self.generic_visit(node)
        self.names_map.pop()
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Transform class definition nodes."""
        self.names_map.append({})
        old_name = node.name
        new_name = next(self.new_class_names)
        node.name = new_name
        self.names_map[-1][old_name] = new_name

        self.generic_visit(node)
        self.names_map.pop()
        return node

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """Transform name nodes."""
        if node.id == 'self' and not self.rename_self:
            return node
        if isinstance(node.ctx, (ast.Store, ast.Param)):
            self._update_name_in_store_context(node)
        elif isinstance(node.ctx, ast.Load):
            self._update_name_in_load_context(node)
        return node

    def visit_Call(self, node: ast.Call) -> ast.Call:
        """Transform call nodes."""
        if isinstance(node.func, ast.Name):
            self._update_name_in_load_context(node.func)
        return self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute) -> ast.Attribute:
        """Transform attribute nodes."""

        if isinstance(node.ctx, ast.Store) and node.attr not in self.names_map[-1]:
            self.names_map[-1][node.attr] = next(self.new_names)
        print(self.names_map)
        print("Attribute: ", node.attr)

        node.attr = self.names_map[-1].get(node.attr, node.attr)
        return self.generic_visit(node)

    def _update_name_in_store_context(self, node: ast.Name) -> None:
        """Update names in the store context."""
        if node.id not in self.names_map[-1]:
            self.names_map[-1][node.id] = next(self.new_names)
        node.id = self.names_map[-1][node.id]

    def _update_name_in_load_context(self, node: ast.Name) -> None:
        """Update names in the load context."""
        for scope in reversed(self.names_map):
            if node.id in scope:
                node.id = scope[node.id]
                break


class TypeHintRemovalTransformer(ast.NodeTransformer):
    """
    AST transformer that removes type hints from the AST.
    """

    def __init__(self, remove: Optional[List[str]] = None) -> None:
        """
        Initialize transformer.

        :param remove: Optional list of hint types to remove. Defaults to removing all types if None.
        """
        if remove is None:
            remove = ["return", "arg", "variable"]
        self.remove = remove

        # Mapping of string identifiers to node type and action
        self.remove_actions = {
            "return": (ast.FunctionDef, self.remove_return_type_hint),
            "arg": (ast.arg, self.remove_arg_type_hint),
            "variable": (ast.AnnAssign, self.remove_variable_type_hint)
        }

    def visit(self, node: ast.AST) -> ast.AST:
        """
        Visit a node in the AST and remove type hints if necessary.

        :param node: The AST node to visit.
        :return: The visited node.
        """
        for hint, (node_type, action) in self.remove_actions.items():
            if hint in self.remove and isinstance(node, node_type):
                node = action(node)
        return self.generic_visit(node)

    @staticmethod
    def remove_return_type_hint(node: ast.FunctionDef) -> ast.FunctionDef:
        """
        Remove return type hint from a function definition node.

        :param node: The function definition node.
        :return: The node with return type hint removed.
        """
        node.returns = None
        return node

    @staticmethod
    def remove_arg_type_hint(node: ast.arg) -> ast.arg:
        """
        Remove argument type hint from an argument node.

        :param node: The argument node.
        :return: The node with argument type hint removed.
        """
        node.annotation = None
        return node

    @staticmethod
    def remove_variable_type_hint(node: ast.AnnAssign) -> ast.Assign:
        """
        Remove variable type hint from an annotated assignment node.

        :param node: The annotated assignment node.
        :return: The node with variable type hint removed.
        """
        node = ast.Assign(targets=[node.target], value=node.value)
        return node



if __name__ == "__main__":
    # Example Usage
    source_code = """
class Foo:
    def bar(self, a, b):
        c = a + b
        self.d = c
        print(self.d)
        def baz(e):
            f = e + 1
            print(f)
        baz(c)
foo = Foo()
foo.bar(1, 2)
"""
    tree = ast.parse(source_code)
    renamer = IdentifierRenamingTransformer(rename_self=True)
    new_tree = renamer.visit(tree)
    new_code = ast.unparse(new_tree)
    print(new_code)
