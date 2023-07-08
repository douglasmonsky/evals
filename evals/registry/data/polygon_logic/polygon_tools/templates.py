import json
from typing import Dict, List
from logger_config import logger


SYSTEM_MESSAGE = "You are starting on an X,Y grid at position (0,0) facing upwards (towards positive Y)." \
                 "You will be given a series of instructions on how to turn and move across the plane." \
                 "Moves will be given in a list of (movement type, movement amount) pairs." \
                 "For Example: [(T, 90), (M, 10), (T, -90), (M, 10)].\n" \
                 "(T, FLOAT) indicates Turning in place <FLOAT> degrees without moving.\n" \
                 "(M, FLOAT) indicates Moving <FLOAT> units in the direction you are currently facing."

USER_MESSAGE = "HERE IS YOUR LIST OF MOVES:{move_list}. {question}"

ANSWER_FORMAT = "Use chain of thought reasoning before answering." \
                "Please enter your final answer in the following format: {final_answer_format}. " \
                "IMPORTANT: DO NOT INCLUDE ANY UNITS IN YOUR ANSWER, PICK ONLY ONE OPTION."


class IncludesEvalTemplate:
    """A class used for creating and storing samples in a particular format.

    Attributes
    ----------
    samples : List[Dict[str, Union[str, List[str]]]]
        List of samples where each sample has some input and an ideal answer.

    Methods
    -------
    create_sample(system_message: str, user_message: str, ideal_answer: str) -> Dict[str, Union[str, List[str]]]:
        Creates a sample with given system message, user message, and ideal answer.

    export_to_jsonl(filename: str):
        Exports all the samples to a jsonl file with the given filename.
    """
    def __init__(self) -> None:
        """Initializes the list of samples as an empty list."""
        self.samples = []

    def create_sample(
        self,
        system_message: str,
        user_message: str,
        ideal_answer: str,
    ) -> Dict[str, str | List[str]]:
        """
        Creates a sample with given system message, user message, and ideal answer.

        Parameters
        ----------
        system_message : str
            The system message for this sample.
        user_message : str
            The user message for this sample.
        ideal_answer : str
            The ideal answer for this sample.

        Returns
        -------
        Sample : dict
            The generated sample.
        """
        sample = {
            "input": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            "ideal": f"[{ideal_answer}]",
        }
        self.samples.append(sample)
        logger.debug(f"Sample created: {sample}")
        logger.info(f"{user_message} -> {ideal_answer}")
        return sample

    def export_to_jsonl(self, filename: str = "samples.jsonl") -> None:
        """
        Exports all the samples to a jsonl file with the given filename.

        Parameters
        ----------
        filename : str
            The name of the file to which the samples will be exported.
        """
        with open(filename, "w") as f:
            for sample in self.samples:
                f.write(json.dumps(sample) + "\n")
