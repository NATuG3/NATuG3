from dataclasses import dataclass
from typing import Type

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
        connected: Whether this NEMid is connected to another NEMid.
        connectmate: NEMid that this NEMid is connected to.
    """

    juncmate: Type["NEMid"] | None = None
    junctable: bool = False
    junction: bool = False

    connectmate: Type["NEMid"] | None = None
    connected: bool = False

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
        return (
            f"NEMid("
            f"pos={tuple(map(lambda i: round(i, 3), self.position()))}, "
            f"angle={round(self.angle, 3)}°, "
            f"junction={str(self.junction).lower()}, "
            f"junctable={str(self.junctable).lower()}, "
            f"connected={str(self.connected).lower()}"
            f")"
        )
