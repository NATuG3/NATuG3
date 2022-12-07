import logging
from dataclasses import dataclass
from typing import Tuple, Type

from constants.directions import DOWN, UP
from helpers import inverse


logger = logging.getLogger(__name__)


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

        The matching point is computed on-the-fly based off of the parent domain's other
        helix for the domain of this point.

        If the point lacks a domain or a strand, None is returned because matching cannot be determined.

        Returns:
            Point: The matching point.
            None: There is no matching point.
        """
        if self.strand is None or self.strand.closed:
            return None
        else:
            # create an easy reference to the entire domains list
            domains = self.domain.parent.parent

            # obtain the index of the domain that this point belongs to
            domain_index = self.domain.index

            # obtain a points array in the formate of
            # [domain#0[up-strand, down-strand], domain#1[up-strand, down-strand], ...]
            domain_points = domains.points()

            # fetch the other strand of the same helix as this point
            if self.strand.up_strand:
                other_strand = domain_points[domain_index][DOWN]
            else:
                other_strand = domain_points[domain_index][UP]

            # since the other strand is a different helix, we must reverse it to find the matching point
            reversed_other_strand = tuple(reversed(other_strand))

            return reversed_other_strand[self.index]

    @staticmethod
    def x_coord_from_angle(angle: float, domain: Type["Domain"]) -> float:
        """
        Compute a new x coord based on the angle and domain of this Point.

        This is a utility function, and doesn't apply to a specific instance of Point.

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

        Returns:
            int: The index of this domain in its respective parent strand.
            None: This point has no parent strand.

        Notes:
            If self.strand is None then this returns None.
        """
        if self.strand is None:
            return None
        else:
            return self.strand.index(self)

    def position(self) -> Tuple[float, float]:
        """
        Obtain coords of the point as a tuple of form (x, z).

        This function merely changes the formatting of the x and z coords to be a zipped tuple.
        """
        return self.x_coord, self.z_coord

    def __repr__(self) -> str:
        """A string representation of the point."""
        return (
            f"NEMid("
            f"pos={tuple(map(lambda i: round(i, 3), self.position()))}), "
            f"angle={round(self.angle, 3)}°,"
            f"matched={self.matched}"
        )

    def __eq__(self, other) -> bool:
        """
        Whether our position and angle is the same as their position and angle.

        If the type of other is not the same as us, this just returns False.
        """
        if not isinstance(other, type(self)):
            return False
        if self.position() == other.position():
            if self.angle == other.angle:
                return True
        return False
