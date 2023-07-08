import math
from typing import List, Tuple
from point import Point


class CartesianPlane:
    def __init__(self, origin: Point = None) -> None:
        """Initializes an entity at origin, facing up (towards positive Y)."""
        if origin is None:
            self.position = Point(0, 0)
        else:
            self.position = origin
        # Entity initially facing up, direction in degrees
        self.direction = 0
        # Keep track of actions taken
        self.actions = []

    def turn(self, angle: float) -> None:
        """Turns the entity by the specified angle, normalizes the direction, and logs the action."""
        self.direction += angle
        # Normalize direction
        self.direction %= 360
        self.actions.append(("T", angle))

    def move(self, distance: float) -> None:
        """
        Moves the entity a certain distance in the direction it's facing.
        """
        rad = math.radians(self.direction)
        self.position.x += math.sin(rad) * distance
        self.position.y += math.cos(rad) * distance
        self.actions.append(("M", distance))

    def perform_actions(self, actions: List[Tuple[str, float]]) -> None:
        """
        Performs a sequence of actions.
        """
        for action, *params in actions:
            if action == "T":
                self.turn(*params)
            elif action == "M":
                self.move(*params)
            else:
                raise ValueError(f"Invalid action {action}")
