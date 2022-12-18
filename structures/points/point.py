import logging
from dataclasses import dataclass
from typing import Tuple, Type, Deque

from constants.directions import DOWN, UP
from utils import inverse

logger = logging.getLogger(__name__)


@dataclass(kw_only=True, slots=True)
class Point:
    """
    A point object.

    Point objects represent parts of/things on helices.

    Attributes:
        x_coord: The x coord of the point.
        z_coord: The z coord of the point.
        angle: Angle from this domain and next domains' line of tangency going
            counterclockwise.
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

    def __post_init__(self):
        """
        Post-init function.

        1) Modulos the angle to be between 0 and 360 degrees.
        2) Ensures that the direction is either UP or DOWN.
        3) Computes the x coord from the angle if the x coord is not provided.
        """
        # Modulo the angle to be between 0 and 360 degrees
        self.angle %= 360

        # Compute the x coord from the angle if the x coord is not provided
        if self.x_coord is None and self.angle is not None and self.domain is not None:
            self.x_coord = self.x_coord_from_angle(self.angle, self.domain)

        # Ensure that the direction is either UP or DOWN
        if self.direction not in (UP, DOWN, None):
            raise ValueError("Direction must be UP or DOWN.")

    def matching(self) -> Type["Point"] | None:
        """
        Obtain the matching point.

        The matching point is computed on-the-fly based off of the parent domain's other
        helix for the domain of this point.

        If the point lacks a domain or a strand, None is returned because matching
        cannot be determined.

        Returns:
            Point: The matching point.
            None: There is no matching point.
        """
        # our domain's parent is a subunit; our domain's subunit's parent is a
        # Domains object we need access to this Domains object in order to locate the
        # matching point
        if (
            self.strand.closed
            or self.domain is None
            or self.domain.parent is None
            or self.domain.parent.parent is None
        ):
            return None
        else:
            # create a reference to the Domains object
            domains = self.domain.parent.parent

            # obtain the helix that we are contained in
            our_helix: Deque[Point] = domains.points()[self.domain.index][
                self.direction
            ]
            # determine our index in our helix
            our_index = our_helix.index(self)

            # obtain the other helix of our domain
            other_helix: Deque[Point] = domains.points()[self.domain.index][
                inverse(self.direction)
            ]
            # since the other strand in our domain is going in the other direction,
            # we reverse the other helix
            other_helix: Tuple[Point] = tuple(reversed(other_helix))

            # obtain the matching point
            matching: Point = other_helix[our_index]

            assert isinstance(matching, type(self))
            assert other_helix is not our_helix
            assert matching not in our_helix

            return matching

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
        # modulo the angle between 0 and 360
        angle %= 360

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
