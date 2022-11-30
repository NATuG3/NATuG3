from dataclasses import dataclass
from types import NoneType
from typing import Union

from constants import bases
from structures.points.point import Point


@dataclass
class Nucleoside(Point):
    """
    Nucleoside object.

    Attributes:
        base: The base of the nucleoside.
        complement: The complementary base of the nucleoside.
    """

    base: Union[bases.A, bases.T, bases.G, bases.C, bases.U, NoneType] = None

    def to_NEMid(self):
        """
        Convert the nucleoside to NEMid type.

        Loses all attributes that point to other Points.
        """
        from structures.points import NEMid

        return NEMid(
            x_coord=self.x_coord,
            z_coord=self.z_coord,
            angle=self.angle,
            direction=self.direction,
            strand=self.strand,
            domain=self.domain,
        )

    @property
    def complement(self) -> str:
        """Return the complement of this base"""

        complements = {
            "A": "T",
            "T": "A",
            "C": "G",
            "G": "C",
            None: None,
        }
        return complements[self.base]

    def __repr__(self) -> str:
        return (
            f"nucleoside("
            f"base(pos={self.position()}), "
            f"angle={round(self.angle, 3)}°, "
            f"base={str(self.base).replace('None', 'unset')}"
            f")"
        )

    def __eq__(self, other):
        """
        Determine equality based on whether the nucleoside base of the other instance matches ours.
        """
        # if it isn't the same type then it cannot be equal
        if not isinstance(other, type(self)):
            return None
        try:
            # if it is the same type and the bases match return true
            if self.base == other.base:
                return True
        # if the .base attribute was missing return false
        except AttributeError:
            return False
