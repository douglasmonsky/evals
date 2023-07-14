import tiktoken
from typing import Any, Dict
from compressors import PythonCompressor
from transformers import IndentationStringTransformer, RemoveDocstringsTransformer,\
    TypeHintRemovalTransformer, RemoveEmptyLinesTransformer


def generate_simple_compression_sample(obj_: Any) -> Dict[str, Any]:
    remove_docstrings = RemoveDocstringsTransformer()
    remove_type_hints = TypeHintRemovalTransformer()
    transform_indentation = IndentationStringTransformer(1)
    remove_empty_lines = RemoveEmptyLinesTransformer()

    code = PythonCompressor(obj_,
                            [remove_docstrings,
                             remove_type_hints,
                             transform_indentation,
                             remove_empty_lines
                             ])
    raw_code = code.code.raw_code
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokenized_raw_code = tokenizer.encode(raw_code)
    raw_token_count = len(tokenized_raw_code)
    compressed_code = code.compress().raw_code
    tokenize_compress_code = tokenizer.encode(compressed_code)
    compressed_token_count = len(tokenize_compress_code)
    dif = compressed_token_count - raw_token_count
    dif_percent = dif / raw_token_count

    original_docs = remove_docstrings.docstrings
    compression_data = {
        "compression_stats": {
                "raw_token_count": raw_token_count,
                "compressed_token_count": compressed_token_count,
                "difference": dif,
                "difference_percent": dif_percent
                 },
        "object": obj_,
        "original_docs": original_docs,
        "compressed_code": compressed_code,
        "raw_code": raw_code,
    }
    print(f"{obj_.__name__} Compressed.\nRaw token count: {raw_token_count}, "
          f"Compressed token count: {compressed_token_count}\n"
          f"Difference: {dif} Tokens ({round(dif_percent, 2) * 100}%)")
    return compression_data


if __name__ == '__main__':
    compression_data = generate_simple_compression_sample(IndentationStringTransformer)
