from dataclasses import dataclass
from typing import Tuple, Type

from helpers import inverse


@dataclass(kw_only=True, slots=True)
class Point:
    """
    A point object.

    Point objects represent parts of/things on helices.

    Attributes:
        x_coord: The x coord of the point.
        z_coord: The z coord of the point.
        angle: Angle from this domain and next domains' line of tangency going counterclockwise.
        direction: The direction of the helix at this point.
        strand: The strand that this point belongs to.
        domain: The domain this point belongs to.
        matching: Point in same domain on other direction's helix across from this one.
        highlighted: Whether the point is highlighted.
    """

    # positional attributes
    x_coord: float = None
    z_coord: float = None
    angle: float = None

    # nucleic acid attributes
    direction: int = None
    strand: Type["Strand"] = None
    domain: Type["Domain"] = None

    # plotting attributes
    highlighted: bool = False

    def matching(self) -> Type["Point"] | None:
        """
        Obtain the matching point.

        Returns:
            Point: The matching point.
            None: There is no matching point.
        """
        if self.strand is None or self.strand.closed:
            return None
        else:
            # obtain our domain's index in respect to the entire Domains object
            domain_index = self.domain.index

            # the parent of a Domain is a Subunit
            # the parent of a Subunit is a Domains
            # Domains.points() returns all points in the structure
            # [#0(up-strand, down_strand), #1(up-strand, down_strand), ...]
            points: Type["Strands"] = self.domain.parent.parent.points()

            # the other strand in the same domain as this point
            # all_domains -> index of this domain -> opposite direction
            other_strand = points[domain_index][inverse(self.direction)]

            # obtain the matching point
            return tuple(reversed(other_strand))[self.index]

    @staticmethod
    def x_coord_from_angle(angle: float, domain: Type["Domain"]) -> float:
        """
        Compute a new x coord based on the angle and domain of this Point.

        Args:
            angle: The angle of the point to compute an x coord for.
            domain: The domain of the point having its x angle computed.

        Returns:
            The x coord.
        """
        theta_interior: float = domain.theta_m
        theta_exterior: float = 360 - theta_interior

        if angle < theta_exterior:
            x_coord = angle / theta_exterior
        else:
            x_coord = (360 - angle) / theta_interior

        # domain 0 lies between [0, 1] on the x axis
        # domain 1 lies between [1, 2] on the x axis
        # ect...
        x_coord += domain.index

        return x_coord

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
