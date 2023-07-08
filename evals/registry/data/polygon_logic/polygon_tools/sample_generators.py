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


class PolygonalLogicSampleGenerator:
    """
    A class used for generating, processing entities and samples.

    Attributes
    ----------
    entities : List[Entity]
        List of entities.
    shape_results : List[Dict[str, Union[int, float, str, List[Tuple[str, float]]]]]
        List of shape results, each represented as a dictionary.

    Methods
    -------
    generate_new_entity() -> Entity:
        Generates a new entity and appends it to the list of entities.

    form_shape(entity: Entity = None, **kwargs: Union[int, float]) -> Dict[str, Any]:
        Forms a shape using an entity and returns the result.

    process_all_entities() -> None:
        Process all entities in self.entities and store the results in self.shape_results.

    generate_samples(option: str) -> None:
        Generates samples based on the results stored in self.shape_results.
    """

    def __init__(self, num_entities: int = 1) -> None:
        """Initializes the list of entities and shape results as empty lists."""
        self.entities: List[Entity] = []
        self.shape_results: List[dict[str, ]] = []
        for _ in range(num_entities):
            self.generate_new_entity()

    def generate_new_entity(self) -> Entity:
        """
        Generates a new entity, appends it to the list of entities, and returns it.

        Returns
        -------
        Entity
            The generated entity.
        """
        entity = Entity()
        self.entities.append(entity)
        return entity

    def form_shape(self, entity: Entity = None,
                   **kwargs: Union[int, float]) -> Dict[str, Any]:
        """
        Forms a shape using an entity and returns the result.

        Parameters
        ----------
        entity : Entity, optional
            The entity used to form a shape. If not given, uses and removes the last entity in self.entities.
        **kwargs : Union[int, float]
            Keyword arguments used to form a shape.

        Returns
        -------
        dict
            The result of the shape formation.
        """
        if entity is None:
            entity = self.entities.pop()
        return entity.form_shape(**kwargs)

    def process_all_entities(self) -> None:
        """
        Processes all entities in self.entities by making them form a shape,
        and stores the result of each entity in self.shape_results.
        """
        self.entities_iter = iter(self.entities)
        while True:
            try:
                entity = next(self.entities_iter)
            except StopIteration:
                break
            shape_info = self.form_shape(entity)
            self.shape_results.append(shape_info)

    def generate_samples(self, option: str) -> None:
        """
        Generates samples based on the results stored in self.shape_results
        and exports these samples to a jsonl file.

        Parameters
        ----------
        option : str
            The option that determines the question and the ideal answer of the sample.
        """
        template = IncludesEvalTemplate()
        options = {
            "shape": f"What is the name of the shape you made. Here is a list of choices {polygon_names.values()}?",
            "area": "What is the area of the shape you made rounded to 2 decimals?",
            "distance_to_origin": "What is the distance from the origin (0,0) to your current position (X, Y)?",
            "current_position": "What is your current position [X, Y]?",
        }
        question = options.get(option)

        for shape_result in self.shape_results:
            user_message = USER_MESSAGE.format(move_list=shape_result["actions"], question=question)
            user_message += "\n" + ANSWER_FORMAT
            ideal_answer = shape_result.get(option)
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