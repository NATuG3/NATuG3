from dataclasses import dataclass
from types import NoneType
from typing import Tuple, Tuple, Union
from constants import bases


@dataclass
class NEMid:
    """Dataclass for a NEMid."""

    # Generic Attributes
    x_coord: float
    z_coord: float
    angle: float

    # NEMid Specific Attributes
    is_junction: bool = False

    def __repr__(self) -> str:
        """Determine what to print when instance is printed directly."""
        return f"NEMid(pos={self.position()}), angle={round(self.angle, 3)}°, is_junction={str(self.is_junction).lower()}"

    def position(self, round_to=3) -> Tuple[float, float]:
        """Return coords of the NEMid as a tuple of form (x, z)"""
        return (round(self.x_coord, round_to), round(self.z_coord, round_to))


@dataclass
class nucleoside:
    """Dataclass for a nucleoside."""

    # Generic Attributes
    x_coord: float
    z_coord: float
    angle: float

    # Base Specific Attributes
    base: Union[bases.A, bases.T, bases.G, bases.C, bases.U, NoneType]

    def __repr__(self) -> str:
        return f"base(pos={self.position()}), angle={round(self.angle, 3)}°, base={str(self.base).replace('None','unset')}"

    def position(self, round_to=3) -> Tuple[float, float]:
        """Return coords of the base as a tuple of form (x, z)"""
        return (round(self.x_coord, round_to), round(self.z_coord, round_to))

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
