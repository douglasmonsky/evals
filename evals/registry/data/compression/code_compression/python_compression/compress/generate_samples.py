from compressors import PythonCompressor
from transformers import IdentifierRenamingTransformer,\
    IndentationStringTransformer, RemoveDocstringsTransformer, TypeHintRemovalTransformer


def main() -> None:
    remove_docstrings = RemoveDocstringsTransformer()
    rename_identifiers = IdentifierRenamingTransformer()
    remove_type_hints = TypeHintRemovalTransformer()
    transform_indentation = IndentationStringTransformer(1)
    code = PythonCompressor(RemoveDocstringsTransformer,
                            [remove_docstrings,
                             rename_identifiers,
                             remove_type_hints,
                             transform_indentation
                             ])
    print(code.compress())


if __name__ == '__main__':
    main()