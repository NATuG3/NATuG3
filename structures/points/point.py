from dataclasses import dataclass
from typing import Tuple, Literal, Type

from constants.directions import *
from structures.domains import Domain


@dataclass(kw_only=True, slots=True)
class Point:
    """
    A point object.

    Point objects represent parts of/things on helices.

    Attributes:
        x_coord: The x coord of the NEMid.
        z_coord: The z coord of the NEMid.
        angle: Angle from this domain and next domains' line of tangency going counterclockwise.
        direction: The direction of the helix at this NEMid.
        strand: The strand that this NEMid belongs to.
        domain: The domain this NEMid belongs to.
        matching: NEMid in same domain on other direction's helix across from this one.
        highlighted: Whether the NEMid is highlighted.
    """

    # positional attributes
    x_coord: float = None
    z_coord: float = None
    angle: float = None

    # nucleic acid attributes
    direction: Literal[UP, DOWN] = None
    strand: Type["Strand"] = None
    domain: Domain = None
    matching: Type["Point"] = None

    # plotting attributes
    highlighted: bool = False

    @property
    def index(self):
        """
        Obtain the index of this domain in its respective parent strand.

        Notes:
            If self.strand is None then this returns None.
        """
        if self.strand is None:
            return None
        else:
            return self.strand.index(self)

    def position(self) -> Tuple[float, float]:
        """Obtain coords of the point as a tuple of form (x, z)."""
        return self.x_coord, self.z_coord

    def __repr__(self) -> str:
        """Determine what to print when instance is printed directly."""
        return (
            f"NEMid("
            f"pos={tuple(map(lambda i: round(i, 3), self.position()))}), "
            f"angle={round(self.angle, 3)}°,"
            f"matched={self.matched}"
        )

    def __eq__(self, other):
        """Whether our position and angle is the same as their position and angle."""
        if not isinstance(other, type(self)):
            return False
        if self.position() == other.position():
            if self.angle == other.angle:
                return True
        return False
