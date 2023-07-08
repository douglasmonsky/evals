from typing import List, Dict, Union, Any

from templates import SYSTEM_MESSAGE, USER_MESSAGE, ANSWER_FORMAT, IncludesEvalTemplate
from entity import Polygon, EntityData
from polygon_names import polygon_names
from plot import plot_polygon
from validation import PolygonValidator


class PolygonalLogicSampleGenerator:
    """
    A class used for generating, processing entities and samples.

    Attributes
    ----------
    polygons : List[Entity]
        List of entities.
    results : List[Dict[str, Union[int, float, str, List[Tuple[str, float]]]]]
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
        self.polygons: List[Polygon] = []
        for _ in range(num_entities):
            self.generate_new_polygon()

    def generate_new_polygon(self) -> Polygon:
        """
        Generates a new entity, appends it to the list of entities, and returns it.

        Returns
        -------
        Entity
            The generated entity.
        """
        entity = Polygon()
        self.polygons.append(entity)
        return entity

    def plot_polygon(self, polygon: Polygon = None) -> EntityData:
        """
        Forms a shape using an entity and returns the result.

        Parameters
        ----------
        polygon : Entity, optional
            The entity used to form a shape. If not given, uses and removes the last entity in self.entities.
        Returns
        -------
        dict
            The result of the shape formation.
        """
        if polygon is None:
            polygon = self.polygons.pop()
        return polygon.form_shape()

    def process_all_polygons(self) -> None:
        """
        Processes all entities in self.polygons by making them form a shape,
        and stores the result of each polygon in self.shape_results.
        """
        for polygon in self.polygons:
            entity_data = self.plot_polygon(polygon)
            polygon.entity_data = entity_data

    def generate_samples(self, option: str, plot: bool = True) -> None:
        """
        Generates samples based on the results stored in self.shape_results
        and exports these samples to a jsonl file.

        Parameters
        ----------
        option : str
            The option that determines the question and the ideal answer of the sample.
        plot : bool
            If True, a plot of the shape will be generated for easier visual validation.
        """
        template = IncludesEvalTemplate()
        validator = PolygonValidator()
        options = {
            "shape":
                {'question': f"What is the name of the shape you made."
                             f" Here is a list of choices {polygon_names.values()}?",
                 'final_answer_format': '[<shape_name.lower()>]'},
            "area":
                {'question': "What is the area of the shape you made?",
                 'final_answer_format': '\n[<area rounded to the nearest int>]\n'},
            "distance_to_origin":
                {'question': "What is the distance from the origin (0,0) to your current position (X, Y)?",
                 'final_answer_format': '\n[<distance rounded to the nearest int\n>]'},
            "current_position":
                {'question': "What is your current position [X, Y]?",
                 'final_answer_format': '\n[<(X,Y)>] where each is rounded to the nearest int\n'}
        }

        option_info = options.get(option)
        question = option_info.get('question')
        final_answer_format = option_info.get('final_answer_format')

        for i, polygon in enumerate(self.polygons):
            entity_data = polygon.entity_data
            user_message = USER_MESSAGE.format(move_list=entity_data.get("actions"), question=question)
            final_answer_format = ANSWER_FORMAT.format(final_answer_format=final_answer_format)
            user_message += "\n" + final_answer_format
            ideal_answer = entity_data.get(option)
            if plot:
                plot_polygon(entity_data, i)
            valid = validator.validate(polygon)
            if valid:
                template.create_sample(
                    system_message=SYSTEM_MESSAGE,
                    user_message=user_message,
                    ideal_answer=ideal_answer,
                )
        template.export_to_jsonl(f"{option}_samples.jsonl")


if __name__ == "__main__":
    generator = PolygonalLogicSampleGenerator(5)
    generator.process_all_polygons()
    generator.generate_samples("shape")
    generator.generate_samples("area")
    # generator.generate_samples("distance_to_origin")
    # generator.generate_samples("current_position")
