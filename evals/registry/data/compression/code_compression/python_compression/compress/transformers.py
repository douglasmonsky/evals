import ast
import string
import itertools


class RemoveDocstringsTransformer(ast.NodeTransformer):
    def __init__(self) -> None:
        self.docstrings = {}

    def handle_docstring(self, node: ast.Name) -> None:
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
            node_name = node.name if hasattr(node, 'name') else 'module'

            # Store the removed docstring in our dictionary, keyed by the name of the node.
            self.docstrings[node_name] = docstring

            # Remove the docstring from the body of the node.
            node.body = node.body[1:]

    def visit(self, node: ast.Name) -> ast.Name:
        # If the node is a function definition, a class definition, or a module, we handle the docstring.
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
            self.handle_docstring(node)

        # Continue the traversal as normal for all nodes.
        return self.generic_visit(node)


class IdentifierRenamingTransformer(ast.NodeTransformer):
    def __init__(self, rename_self: bool = False) -> None:
        # create iterators that generate new names for variables and classes
        self.new_var_names = self.generate_names(string.ascii_lowercase)
        self.new_class_names = self.generate_names(string.ascii_uppercase)
        # create stacks of dictionaries to map old variable and class names to new names in different scopes
        self.var_names_map = [{}]
        self.class_names_map = [{}]
        # Store whether to rename 'self'
        self.rename_self = rename_self

    @staticmethod
    def generate_names(alphabet: str) -> str:
        # Generate names by cycling through letters and appending numbers
        for size in itertools.count(1):
            for s in itertools.product(alphabet, repeat=size):
                yield "".join(s)

    def visit_FunctionDef(self, node: ast.Name) -> ast.Name:
        # Push a new dictionary onto the stack when entering a new function definition
        self.var_names_map.append({})
        # Rename the function itself
        node.name = next(self.new_var_names)
        # Rename the function arguments, except 'self' if rename_self is False
        for arg in node.args.args:
            if arg.arg == 'self' and not self.rename_self:
                continue
            self.var_names_map[-1][arg.arg] = next(self.new_var_names)
            arg.arg = self.var_names_map[-1][arg.arg]
        # Process the function body
        self.generic_visit(node)
        # Pop the top dictionary off the stack when leaving the function definition
        self.var_names_map.pop()
        return node

    def visit_ClassDef(self, node: ast.Name) -> ast.Name:
        # Push a new dictionary onto the stack when entering a new class definition
        self.var_names_map.append({})
        # Rename the class itself
        new_class_name = next(self.new_class_names)
        self.class_names_map[-1][node.name] = new_class_name
        node.name = new_class_name
        # Process the class body
        self.generic_visit(node)
        # Pop the top dictionary off the stack when leaving the class definition
        self.var_names_map.pop()
        return node

    def visit_Name(self, node: ast.Name) -> ast.Name:
        if node.id == 'self' and not self.rename_self:
            return node
        if isinstance(node.ctx, (ast.Store, ast.Param)):
            self._update_name_in_store_context(node)
        elif isinstance(node.ctx, ast.Load):
            self._update_name_in_load_context(node)
        return node

    def _update_name_in_store_context(self, node: ast.Name) -> ast.Name:
        if node.id not in self.var_names_map[-1]:
            self.var_names_map[-1][node.id] = next(self.new_var_names)
        node.id = self.var_names_map[-1][node.id]

    def _update_name_in_load_context(self, node: ast.Name) -> None:
        for scope in reversed(self.var_names_map):
            if node.id in scope:
                node.id = scope[node.id]
                break
        for scope in reversed(self.class_names_map):
            if node.id in scope:
                node.id = scope[node.id]
                break


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
