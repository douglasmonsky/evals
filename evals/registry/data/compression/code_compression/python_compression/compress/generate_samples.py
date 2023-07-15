import json
import tiktoken
from typing import Any, Dict, List
from compressors import PythonCompressor
from transformers import IndentationStringTransformer, RemoveDocstringsTransformer,\
    TypeHintRemovalTransformer, RemoveEmptyLinesTransformer


remove_docstrings = RemoveDocstringsTransformer()
remove_type_hints = TypeHintRemovalTransformer()
transform_indentation = IndentationStringTransformer(1)
remove_empty_lines = RemoveEmptyLinesTransformer()

original_task_description = "Write docstrings for the provided code.\n" \
                                "The docstrings should be as descriptive as possible.\n" \
                                "Before answering, reason in a step-by-step chain of thought," \
                                " then conclude with the answer in the following format:\n" \
                                "Final Docstring: {" \
                                "<class/function/method 1 name>: <corresponding_docstring>," \
                                "<class/function/method 2 name>: <corresponding_docstring>," \
                                " ...}\n"



def generate_simple_compression_sample(obj_: Any) -> Dict[str, Any]:
    """Generate a simple compression sample for the given object."""
    code = PythonCompressor(obj_,
                            [remove_docstrings,
                             remove_type_hints,
                             transform_indentation,
                             remove_empty_lines
                             ])
    raw_code = code.code.raw_code
    tokenizer = tiktoken.get_encoding("cl100k_base")
    tokenized_raw_code = tokenizer.encode(raw_code, disallowed_special=())
    raw_token_count = len(tokenized_raw_code)
    compressed_code = code.compress().raw_code
    tokenize_compress_code = tokenizer.encode(compressed_code, disallowed_special=())
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
    remove_docstrings.clear_docstrings()
    return compression_data


class GranularBattleEvalTemplate:
    samples = []

    def create_sample(
        self,
        input1: str,
        input2: str,
        original_task_description: str,
        ideal: str,
    ) -> Dict[str, str | List[str]]:
        sample = {
            "input1": input1,
            "input2": input2,
            "original_task_description": original_task_description,
            "ideal": ideal,
        }
        self.samples.append(sample)
        return sample

    def export_to_jsonl(self, filename: str = "samples.jsonl") -> None:
        with open(filename, "w") as f:
            for sample in self.samples:
                f.write(json.dumps(sample) + "\n")


if __name__ == '__main__':
    import nltk
    eval_creator = GranularBattleEvalTemplate()

    list_of_objects = [json.JSONDecoder, json.JSONEncoder, json.dumps, json.loads,
                       nltk.tokenize, nltk.tokenize.word_tokenize, nltk.OrderedDict,
                       nltk.tokenize.treebank.TreebankWordTokenizer, tiktoken.Encoding,
                       tiktoken.encoding_for_model]
    for obj in list_of_objects:
        compression_data = generate_simple_compression_sample(obj)
        input_1 = f"{original_task_description}\nCode:\n{compression_data['raw_code']}"
        input_2 = f"{original_task_description}\nCode:\n{compression_data['compressed_code']}"
        ideal = f"Final Docstring: {compression_data['original_docs']}"
        eval_creator.create_sample(original_task_description=original_task_description,
                                   input1=input_1,
                                   input2=input_2,
                                   ideal=ideal,
                                   )
    eval_creator.export_to_jsonl("simple_python_compression.jsonl")
