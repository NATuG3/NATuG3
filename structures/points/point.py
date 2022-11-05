from dataclasses import dataclass
from typing import Tuple, Literal

from constants.directions import *


@dataclass
class Point:
    """
    NEMid object.

    Attributes:
        x_coord (float): The x coord of the NEMid.
        z_coord (float): The z coord of the NEMid.
        angle (float): Angle from this domain and next domains' line of tangency going counterclockwise.
        direction (Literal[UP, DOWN]): The direction of the helix at this NEMid.
    """

    x_coord: float
    z_coord: float
    angle: float
    direction: Literal[UP, DOWN]
    prime: Literal[TOWARDS_START, TOWARDS_END]

    def __post_init__(self):
        self.highlighted = False

    def position(self) -> Tuple[float, float]:
        """
        Obtain coords of the point as a tuple of form (x, z).
        """
        return self.x_coord, self.z_coord

    def __repr__(self) -> str:
        """
        Determine what to print when instance is printed directly.
        """
        return (
            f"NEMid("
            f"pos={tuple(map(lambda i: round(i, 3), self.position()))}), "
            f"angle={round(self.angle, 3)}°,"
            f"matched={self.matched}"
        )

    def __eq__(self, other):
        print(self, other)
        if not isinstance(other, type(self)):
            return False
        if self.position() == other.position():
            if self.angle == other.angle:
                return True
        return False
