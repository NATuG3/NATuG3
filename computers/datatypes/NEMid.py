from dataclasses import dataclass
from types import NoneType
from typing import Tuple, Union, Literal
from typing import TypeVar

from constants.directions import *


@dataclass
class NEMid:
    """
    NEMid object.

    Attributes:
        x_coord (float): The x coord of the NEMid.
        z_coord (float): The z coord of the NEMid.
        angle (float): Angle from this domain and next domains' line of tangency going counterclockwise.
        direction (Literal[UP, DOWN]): The direction of the helix at this NEMid.
        matching (NEMid): NEMid in same domain on other direction's helix across from this one.
        juncmate (Union[NEMid, None]): NEMid that can this NEMid can conjunct-with. NoneType if this no NEMid overlaps.
        junction (bool): Whether this NEMid is at the site of an active junction.
        junctable (bool): Whether this NEMid overlaps another NEMid and can thus can conjunct.
    """

    # Generic Attributes
    x_coord: float
    z_coord: float
    angle: float
    direction: Literal[UP, DOWN]
    matching: TypeVar = None

    # NEMid Specific Attributes
    juncmate: Union[TypeVar, NoneType] = None
    junction: bool = False
    junctable: bool = False

    @property
    def position(self) -> Tuple[float, float]:
        """Return coords of the base as a tuple of form (x, z)"""
        return self.x_coord, self.z_coord

    def __repr__(self) -> str:
        """Determine what to print when instance is printed directly."""
        return (
            f"NEMid("
            f"pos={tuple(map(lambda i: round(i, 3), self.position))}), "
            f"angle={round(self.angle, 3)}°, "
            f"junction={str(self.junction).lower()}, "
            f"junctable={str(self.junctable).lower()}"
        )
