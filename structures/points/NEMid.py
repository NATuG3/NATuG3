from dataclasses import dataclass
from typing import Type, Tuple

from structures.points.point import Point


@dataclass
class NEMid(Point):
    """
    NEMid object.

    Attributes:
        juncmate: NEMid that can this NEMid can conjunct-with. NoneType if this no NEMid overlaps.
        junction: Whether this NEMid is at the site of an active junction.
        junctable: Whether this NEMid overlaps another NEMid and can thus can conjunct.
    """

    juncmate: Type["NEMid"] | None = None
    junction: bool = False
    junctable: bool = False

    def to_nucleoside(self) -> Tuple[Type["Nucleoside"], Type["Nucleoside"]]:
        """Convert the nucleoside to NEMid type."""
        from structures.points import Nucleoside

        new_matching = Nucleoside(
            x_coord=self.matching.x_coord,
            z_coord=self.matching.z_coord,
            angle=self.matching.angle,
            direction=self.matching.direction,
            strand=self.matching.strand,
            domain=self.matching.domain,
        )

        new_self = Nucleoside(
            x_coord=self.x_coord,
            z_coord=self.z_coord,
            angle=self.angle,
            direction=self.direction,
            strand=self.strand,
            domain=self.domain,
        )

        return new_self, new_matching

    def __repr__(self) -> str:
        """Determine what to print when instance is printed directly."""
        return (
            f"NEMid("
            f"pos={tuple(map(lambda i: round(i, 3), self.position()))}, "
            f"angle={round(self.angle, 3)}°, "
            f"junction={str(self.junction).lower()}, "
            f"junctable={str(self.junctable).lower()}"
            f")"
        )
