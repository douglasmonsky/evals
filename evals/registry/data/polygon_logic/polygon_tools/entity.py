import random
from typing import List, Tuple, Optional, TypedDict
from point import Point
from polygon_names import polygon_names
from cartesianplane import CartesianPlane


class EntityData(TypedDict):
    actions: List[str]
    shape: str
    distance_to_origin: float
    area: float
    current_position: Tuple[float, float]


class Polygon:
    def __init__(self, sides: Optional[int] = None, distance: Optional[float] = None,
                 starting_point: Point = None) -> None:
        if starting_point is None:
            starting_point = Point(0, 0)
        self.vertices = [starting_point]
        self.sides = sides
        self.distance = distance
        # Polygon should belong to grid not the other way around, REFACTOR LATER
        self.grid = CartesianPlane(starting_point)
        self.entity_data: EntityData = {}

    @staticmethod
    def random_sides() -> int:
        """Generates a random number between 3 and 20 for sides"""
        return random.randint(3, 20)

    @staticmethod
    def random_distance() -> float:
        """Generates a random value between 0.5 and 100 for distance"""
        return random.uniform(0.5, 100)

    def calculate_area(self) -> float:
        """
        Calculates area of the polygon formed by the vertices.

        Returns
        -------
        float
            The area of the polygon. If less than 3 vertices, returns 0.
        """
        n = len(self.vertices)
        if n < 3:
            return 0

        # Shoelace formula/Gauss's Area formula
        area = sum(
            self.vertices[i].x * self.vertices[(i + 1) % n].y
            - self.vertices[(i + 1) % n].x * self.vertices[i].y
            for i in range(n)
        )
        return round(abs(area) / 2, 2)

    def form_shape(self) -> EntityData:
        # The function forms a shape by moving the entity in a specific pattern.
        if self.sides is None:
            self.sides = random.randint(3, 20)
        if self.sides < 3:
            raise ValueError("Not enough sides to form shape.")

        if self.distance is None:
            self.distance = round(random.uniform(0.5, 100), 2)
        if self.distance <= 0:
            raise ValueError("Distance too small.")

        turn_angle = 360 / self.sides

        for _ in range(self.sides):
            self.grid.move(self.distance)
            self.vertices.append(Point(self.grid.position.x, self.grid.position.y))
            self.grid.turn(turn_angle)

        result: EntityData = {
            "actions": self.grid.actions,
            "shape": polygon_names.get(self.sides, f"{self.sides}-sided polygon"),
            "distance_to_origin": self.grid.position.distance_to_origin(),
            "area": self.calculate_area(),
            "current_position": (round(self.grid.position.x), round(self.grid.position.y)),
        }
        self.entity_data = result
        return result
