import math
import random
from typing import List, Tuple, Dict, Optional, Union
from point import Point
from polygon_names import polygon_names


class Entity:
    """
    A class that represents an Entity which can move and form shapes in
    a two-dimensional Euclidean space.


    Attributes
    ----------
    position : Point
        The current position of the Entity on 2D space (default is Point(0,0))
    direction : float
        The direction in which the Entity is facing (initially 0 degrees)
    vertices : list of Points
        The vertices of the polygon formed by movement of the Entity
    actions : list of tuples
        The actions performed by the Entity. Format: ('Action', value)


    Methods
    -------
    turn(angle: float):
        Turns the entity in space by a given angle
    move(distance: float):
        Moves the entity in space by a certain distance
    calculate_polygon_area():
        Calculates the area of the polygon formed by Entity's movement
    perform_actions(actions: [tuple]):
        Perform a list of actions
    _calculate_turn_angle(sides: int) -> float:
        Calculate the angle needed for a specific number of polygon sides
    _perform_extra_moves(extra_moves: int, distance: float):
        Performs extra moves or turns beyond the required to form the shape
    form_shape(sides: int, distance: float, extra_moves: int) -> dict:
        Makes the entity form a shape, by default a random polygon
    """

    def __init__(self) -> None:
        """Initializes an entity at origin, facing up (towards positive Y)."""
        self.position = Point(0, 0)
        # Entity initially facing up, direction in degrees
        self.direction = 0
        # Keep track of polygon vertices
        self.vertices = []
        # Keep track of actions taken
        self.actions = []

    def turn(self, angle: float) -> None:
        """Turns the entity by the specified angle, normalizes the direction, and logs the action."""
        self.direction += angle
        # Normalize direction
        self.direction %= 360
        self.actions.append(("T", round(angle, 2)))

    def move(self, distance: float) -> None:
        """
        Moves the entity a certain distance in the direction it's facing.

        Parameters
        ----------
        distance : float
            The distance to move.
        """
        # Convert to radians
        rad = math.radians(self.direction)
        self.position.x += math.sin(rad) * distance
        self.position.y += math.cos(rad) * distance
        self.vertices.append(Point(self.position.x, self.position.y))
        self.actions.append(("M", distance))

    def calculate_polygon_area(self) -> float:
        """
        Calculates the area of the polygon formed by the vertices.

        Returns
        -------
        float
            The area of the polygon. If less than 3 vertices, returns 0.
        """
        n = len(self.vertices)
        if n < 3:
            return 0

        area = sum(
            self.vertices[i].x * self.vertices[(i + 1) % n].y
            - self.vertices[(i + 1) % n].x * self.vertices[i].y
            for i in range(n)
        )
        return round(abs(area) / 2, 2)

    def perform_actions(self, actions: List[Tuple[str, float]]) -> None:
        """
        Performs a sequence of actions. Each action is a tuple where
        the first element is a string indicating the action type ("T" for turn, "M" for move),
        and the rest are parameters for the action.

        Parameters
        ----------
        actions : list of tuple
            The actions to perform.
        """
        for action, *params in actions:
            if action == "T":
                self.turn(*params)
            elif action == "M":
                self.move(*params)
            else:
                raise ValueError(f"Invalid action {action}")

    @staticmethod
    def _calculate_turn_angle(sides: int) -> float:
        """
        Calculates the angle needed to form a polygon with the given number of sides.
        """
        return round(360 / sides, 2)

    def _perform_extra_moves(self, extra_moves: int, distance: float) -> None:
        """
        Performs extra moves or turns at random for added complexity.

        Parameters
        ----------
        extra_moves : int
            The number of extra moves to perform.
        distance : float
            The distance for each move.
        """
        for _ in range(extra_moves):
            action = random.choice(["T", "M"])
            if action == "T":
                self.turn(random.uniform(-180, 180))
            else:
                self.move(distance)

    def form_shape(
            self,
            sides: Optional[int] = None,
            distance: Optional[float] = None,
            extra_moves: Optional[int] = None,
    ) -> Dict[str, Union[List[Tuple[str, float]], str, float]]:
        """
        The function forms a shape by moving the entity in a specific pattern.

        Parameters
        ----------
        sides : int, optional
            The number of sides for the shape to form. If not given, a random number
            between 3 and 20 is selected.
        distance : float, optional
            The distance of each move. If not given, a random value
            between 0.5 and 100 is selected.
        extra_moves : int, optional
            The number of extra moves/turns at the end. If not given, a random number
            between 0 and 4 is selected.

        Returns
        -------
        dict
            A dictionary containing the actions taken to form the shape, the name of
            the shape, the shortest distance to the origin, and the area of the shape.
        """

        # If sides was not given, generate a random number between 3 and 20
        if sides is None:
            sides = random.randint(3, 20)
        if sides < 3:
            raise ValueError("Not enough sides to form shape.")

        # If distance was not given, generate a random value between 0.5 and 100
        if distance is None:
            distance = round(random.uniform(0.5, 100), 2)
        if distance <= 0:
            raise ValueError("Distance too small.")

        # If extra_moves was not given, generate a random number between 0 and 4
        if extra_moves is None:
            extra_moves = random.randint(0, 4)

        # Calculate the turn angle based on the number of sides
        turn_angle = self._calculate_turn_angle(sides)

        # Perform the moves and turns to form the shape
        for _ in range(sides):
            self.move(distance)
            self.turn(turn_angle)

        # Perform any extra moves or turns
        if extra_moves:
            self._perform_extra_moves(extra_moves, distance)

        # Calculate and collect the results
        result = {
            "actions": self.actions,
            "shape": polygon_names.get(sides, f"{sides}-sided polygon"),
            "distance_to_origin": self.position.distance_to_origin(),
            "area": self.calculate_polygon_area(),
            "current_position": f"{round(self.position.x, 2)}, {round(self.position.y, 2)}",
        }

        return result
