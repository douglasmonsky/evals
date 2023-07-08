import json
from typing import List, Dict, Union, Any
from logger_config import logger
from entity import Entity
from polygon_names import polygon_names


SYSTEM_MESSAGE = "You are starting on an X,Y grid at position (0,0) facing upwards (towards positive Y)." \
                 "You will be given a series of instructions on how to turn and move across the plane." \
                 "Moves will be given in a list of (movement type, movement amount) pairs." \
                 "For Example: [(T, 90), (M, 10), (T, -90), (M, 10)].\n" \
                 "(T, FLOAT) indicates Turning in place <FLOAT> degrees without moving.\n" \
                 "(M, FLOAT) indicates Moving <FLOAT> units in the direction you are currently facing." \

USER_MESSAGE = "HERE IS YOUR LIST OF MOVES:{move_list}. {question}"

ANSWER_FORMAT = "Use chain of thought reasoning before answering." \
                "Please enter your final answer in the following format: [<answer>]. " \
                "IMPORTANT: DO NOT INCLUDE ANY UNITS IN YOUR ANSWER, PICK ONLY ONE OPTION."


class IncludesEvalTemplate:

    def __init__(self) -> None:
        self.samples = []

    def create_sample(
        self,
        system_message: str,
        user_message: str,
        ideal_answer: str,
    ) -> Dict[str, str | List[str]]:
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
        with open(filename, "w") as f:
            for sample in self.samples:
                f.write(json.dumps(sample) + "\n")


class PolygonalLogicSampleGenerator:

    def __init__(self, num_entities: int = 1) -> None:
        self.entities: List[Entity] = []
        self.shape_results: List[dict[str,]] = []
        for _ in range(num_entities):
            self.generate_new_entity()


    def generate_new_entity(self) -> Entity:
        entity = Entity()
        self.entities.append(entity)
        return entity

    def form_shape(self, entity: Entity = None,
                   **kwargs: Union[int, float]) -> Dict[str, Any]:
        if entity is None:
            entity = self.entities.pop()
        return entity.form_shape(**kwargs)

    def process_all_entities(self) -> None:
        while self.entities:
            shape_info = self.form_shape()
            self.shape_results.append(shape_info)

    def generate_samples(self, option: str) -> None:
        template = IncludesEvalTemplate()
        options = {
            "shape": f"What is the name of the shape you made. Here is a list of choices {polygon_names.values()}?",
            "area": "What is the area of the shape you made rounded to 2 decimals?",
            "distance_to_origin": "What is the distance from the origin (0,0) to your current position (X, Y)?",
            "current_position": "What is your current position [X, Y]?",
        }
        question = options[option]

        for shape_result in self.shape_results:
            user_message = USER_MESSAGE.format(move_list=shape_result["actions"], question=question)
            user_message += "\n" + ANSWER_FORMAT
            ideal_answer = shape_result[option]
            template.create_sample(
                system_message=SYSTEM_MESSAGE,
                user_message=user_message,
                ideal_answer=ideal_answer,
            )
        template.export_to_jsonl(f"{option}_samples.jsonl")


if __name__ == "__main__":
    generator = PolygonalLogicSampleGenerator(100)
    generator.process_all_entities()
    generator.generate_samples("shape")
    generator.generate_samples("area")
    generator.generate_samples("distance_to_origin")
    generator.generate_samples("current_position")