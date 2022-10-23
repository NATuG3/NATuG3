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

    # Generic Attributes
    x_coord: float
    z_coord: float
    angle: float
    direction: Literal[UP, DOWN]

    @property
    def matched(self) -> bool:
        """
        Returns whether if there is point on the complementary helix that matches this NEMid.
        """
        return bool(self.matching)

    @property
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
            f"pos={tuple(map(lambda i: round(i, 3), self.position))}), "
            f"angle={round(self.angle, 3)}°,"
            f"matched={self.matched}"
        )
