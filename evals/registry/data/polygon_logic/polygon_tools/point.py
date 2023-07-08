import math


class Point:
    """
    A class used to represent a point in a two-dimensional Euclidean space.

      Attributes
        ----------
        x : float
            the x-coordinate of the point (default 0.0)
        y : float
            the y-coordinate of the point (default 0.0)
      Methods
        -------
        distance_to_origin(): calculates the Euclidean distance from this point to the origin (0, 0).
    """

    def __init__(self, x: float = 0, y: float = 0) -> None:
        """
        Constructs all the necessary attributes for the Point object.
        x : float the x-coordinate of the point (default 0.0)
        y : float the y-coordinate of the point (default 0.0)
        """
        self.x = x
        self.y = y

    def distance_to_origin(self) -> float:
        """
        Calculates the Euclidean distance from this point to the origin (0, 0)

        Returns
        -------
        The distance from the point to the origin : float
        """
        return round(math.sqrt(self.x**2 + self.y**2), 2)
