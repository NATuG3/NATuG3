from dataclasses import dataclass
from types import NoneType
from typing import TypeVar, Type, Tuple
from typing import Union

from structures.domains import Domain
from structures.points.point import Point


@dataclass(slots=True)
class NEMid(Point):
    """
    NEMid object.

    Attributes:
        domain (Domain or None): The domain this NEMid belongs to.
        matching (NEMid or None): NEMid in same domain on other direction's helix across from this one.
        juncmate (NEMid or None): NEMid that can this NEMid can conjunct-with. NoneType if this no NEMid overlaps.
        junction (bool): Whether this NEMid is at the site of an active junction.
        junctable (bool): Whether this NEMid overlaps another NEMid and can thus can conjunct.
        strand (list or None): The strand that this NEMid belongs to.
        color (tuple or None): If not none then this NEMid is forced to be this color.
    """

    domain: Domain = None
    matching: Type["NEMid"] = None
    juncmate: Type["NEMid"] | None = None
    junction: bool = False
    junctable: bool = False
    strand: None | Type["Strand"] = None
    color: Tuple[int, int, int] | None = None

    @property
    def index(self):
        """
        Obtain the index of this domain in its respective parent strand.

        Notes:
            If self.strand is None then this returns None.
        """
        if self.strand is None:
            return None
        return self.strand.items.index(self)

    def __hash__(self):
        hashed = 0
        hashed += hash(self.x_coord)
        hashed += hash(self.z_coord)
        hashed += hash(self.direction)
        hashed += hash(self.prime)
        return hashed

    def __repr__(self) -> str:
        """Determine what to print when instance is printed directly."""
        return (
            f"NEMid("
            f"pos=({tuple(map(lambda i: round(i, 3), self.position()))}), "
            f"angle={round(self.angle, 3)}°, "
            f"junction={str(self.junction).lower()}, "
            f"junctable={str(self.junctable).lower()}"
            f")"
        )
