from dataclasses import dataclass
from typing import Literal, Tuple


@dataclass
class domain:
    """
    Domain storage object.

    Attributes:
        interjunction_multiple (int): The angle between two junctions on a double helix. Integer multiple of characteristic angle.
        switch_angle_multiple (int): Strand switch angle per domain transition. Integer multiple of strand switch angle.
    """

    interjunction_multiple: int
    switch_angle_multiple: int


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
        return f"NEMid(pos={self.position()}), angle={self.angle}°, is_junction={str(self.is_junction).lower()}"

    def position(self, round_to=3) -> Tuple[float, float]:
        """Return coords of the NEMid as a tuple of form (x, z)"""
        return (round(self.x_coord, round_to), round(self.z_coord, round_to))

    def to_base(self, base_height: float, base: Literal["a", "t", "g", "c", "u"]):
        """Convert the NEMid to a base"""
        return base(self.x_coord, self.z_coord - (base_height / 2), self.angle, base)


@dataclass
class base:
    """Dataclass for a base."""

    # Generic Attributes
    x_coord: float
    z_coord: float
    angle: float

    # Base Specific Attributes
    nucleotide: Literal["a", "t", "g", "c", "u", None]

    def __repr__(self) -> str:
        return f"base(pos={self.position()}), angle={self.angle}°, nucleotide={str(self.nucleotide).replace('None','unset')}"

    def position(self, round_to=3) -> Tuple[float, float]:
        """Return coords of the base as a tuple of form (x, z)"""
        return (round(self.x_coord, round_to), round(self.z_coord, round_to))

    def complement(self) -> str:
        "Return the complement of this base"
        complements = {
            "a": "t",
            "t": "a",
            "u": "a",
            "a": "u",
            "c": "g",
            "g": "c",
        }
        return complements[self.nucleotide]

    def to_NEMid(self, base_height: float, is_junction=False):
        """Convert the base to a NEMid"""
        return NEMid(
            self.x_coord,
            self.z_coord - (base_height / 2),
            self.angle,
            is_junction=is_junction,
        )
