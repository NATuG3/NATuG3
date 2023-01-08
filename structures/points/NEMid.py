from dataclasses import dataclass
from typing import Type

from constants.directions import UP
from structures.points.point import Point


@dataclass
class NEMid(Point):
    """
    NEMid object.

    Attributes:
        junctable: Whether this NEMid overlaps another NEMid and can thus can conjunct.
        juncmate: NEMid that can this NEMid can conjunct-with. NoneType if this no
            NEMid overlaps.
        junction: Whether this NEMid is a member of an active junction.
    """

    juncmate: Type["NEMid"] | None = None
    junctable: bool = False
    junction: bool = False

    def to_nucleoside(self):
        """
        Convert the nucleoside to NEMid type.

        Loses all attributes that point to other Points.
        """
        from structures.points import Nucleoside

        return Nucleoside(
            x_coord=self.x_coord,
            z_coord=self.z_coord,
            angle=self.angle,
            direction=self.direction,
            strand=self.strand,
            domain=self.domain,
        )

    def __repr__(self) -> str:
        """Determine what to print when instance is printed directly."""
        properties = {
            "pos": tuple(map(lambda i: round(i, 3), self.position())),
            "angle": round(self.angle, 3),
            "direction": "UP" if self.direction == UP else "DOWN",
            "junctable": self.junctable,
            "juncmate": self.juncmate,
            "junction": self.junction,
            "domain": self.domain,
            "index": self.index,
        }
        # Create a string in the format NEMid(key1=value1, key2=value2, ...)
        return (
            f"NEMid"
            f"({', '.join(f'{key}={value}' for key, value in properties.items())})"
        )
