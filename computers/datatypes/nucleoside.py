from dataclasses import dataclass
from types import NoneType
from typing import Tuple, Union

from constants import bases


@dataclass
class Nucleoside:
    """Dataclass for a nucleoside."""

    # Generic Attributes
    x_coord: float
    z_coord: float
    angle: float

    # Base Specific Attributes
    base: Union[bases.A, bases.T, bases.G, bases.C, bases.U, NoneType]

    @property
    def position(self) -> Tuple[float, float]:
        """Return coords of the base as a tuple of form (x, z)"""
        return self.x_coord, self.z_coord

    def complementary_base(self) -> str:
        "Return the complement of this base"
        complements = {
            "A": "T",
            "T": "A",
            "U": "A",
            "A": "U",
            "C": "G",
            "G": "C",
        }
        return complements[self.nucleoside]

    def __repr__(self) -> str:
        return f"base(pos={self.position()}), angle={round(self.angle, 3)}°, base={str(self.base).replace('None', 'unset')}"

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return None
        try:
            if self.base == other.base:
                return True
        except AttributeError:
            return False
