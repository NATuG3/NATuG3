from dataclasses import dataclass
from types import NoneType
from typing import Union, TypeVar

from computers.datatypes.point import Point
from constants import bases


@dataclass(slots=True)
class Nucleoside(Point):
    """
    Nucleoside object.

    Attributes:
        matching (NEMid): NEMid in same domain on other direction's helix across from this one.
        base (Union["A", "T", "G", "C", "U"]): The base of the nucleoside.
        complement (Union["A", "T", "G", "C", "U"]): The complementary base of the nucleoside.
    """

    base: Union[bases.A, bases.T, bases.G, bases.C, bases.U, NoneType]
    matching: TypeVar = None

    @property
    def complement(self) -> str:
        "Return the complement of this base"
        complements = {
            "A": "T",
            "T": "A",
            "C": "G",
            "G": "C",
        }
        return complements[self.base]

    def __repr__(self) -> str:
        return (
            f"nucleoside("
            f"base(pos={self.position}), "
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
