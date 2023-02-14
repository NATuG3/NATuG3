import logging
from dataclasses import dataclass, field
from math import dist
from typing import Tuple, Type, List, Iterable
from uuid import uuid1

import pandas as pd

import settings
from constants.directions import DOWN, UP
from utils import inverse, rgb_to_hex

logger = logging.getLogger(__name__)


@dataclass
class PointStyles:
    """
    A container for the styles of a Point.

    Attributes:
        point: The point that the styles are for.
        symbol: The symbol of the Point. Either a subset of pyqtgraph symbols or a str.
        size: The size of the symbol. This is in pixels.
        rotation: The rotation of the symbol. This only is checked when the symbol
            isn't a default symbol (is not in all_symbols). This is in degrees.
        fill: The color of the Point. Tuple of (r, g, b) values.
        outline: The color of the outline of the Point. Tuple of (color, width).

    Methods:
        set_defaults: Automatically set the color of the Point.
        highlight: Highlight the point.
        select: Select the point.
        as_str: Return the styles as a string.
        from_str: Set the styles from a string.
    """

    point: "Point" = None
    symbol: str = None
    size: int = None
    rotation: float = None
    fill: Tuple[int, int, int] = None
    outline: Tuple[Tuple[int, int, int], float] = None, None
    state = "default"

    all_states = ("default", "highlighted", "selected")
    all_symbols = ("o", "t", "t1", "t2", "t3", "s", "p", "h", "star", "+", "d", "x")

    def is_state(self, state: str):
        """Return whether the point is in the given state."""
        return self.state == state

    def change_state(self, state: str):
        """Set the state of the point."""
        self.state = state
        self.reset()

    def symbol_is_custom(self):
        """Return whether the symbol is a custom symbol."""
        return self.symbol not in self.all_symbols

    def reset(self):
        """
        Automatically set the styles of the point based on the state.
        """
        from structures.points import Nucleoside, NEMid
        from ui.plotters.utils import dim_color

        strand, point = self.point.strand, self.point  # Create easy references

        if self.point.strand is None:
            return
        if self.state == "highlighted":
            self.fill = settings.colors["highlighted"]
            self.size = 18
            self.rotation = 0
            self.outline = dim_color(self.fill, 0.7), 1
        elif self.state == "selected":
            self.fill = settings.colors["selected"]
            self.size = 18
            self.rotation = 0
            self.outline = dim_color(self.fill, 0.7), 1
        elif self.state == "default":
            if isinstance(point, Nucleoside):
                if point.base is None:
                    # Baseless nucleosides are normally colored
                    self.fill = dim_color(strand.styles.color.value, 0.9)

                    # If strand color is light use dark outline else use a light outline
                    self.outline = (
                        ((200, 200, 200), 0.65)
                        if (sum(strand.styles.color.value) < (255 * 3) / 2)
                        else ((0, 0, 0), 0.5)
                    )

                    # Since there is no base make the symbol an arrow
                    self.symbol = "t1" if point.direction is UP else "t"

                    # Since there's no base make the point smaller
                    self.size = 7
                else:
                    # Based nucleosides are dimly colored
                    self.fill = dim_color(strand.styles.color.value, 0.3)
                    self.outline = dim_color(strand.styles.color.value, 0.5), 0.3

                    # Since there is a base make the symbol the base
                    self.symbol = point.base  # type: ignore

                    # Make the base orient based off of the symbol direction
                    self.rotation = -90 if point.direction is UP else 90

                    # Since there is a base make it bigger
                    self.size = 9
            elif isinstance(point, NEMid):
                # All NEMids share some common styles
                self.symbol = "t1" if point.direction is UP else "t"
                self.rotation = 0
                self.size = 6

                if point.junctable:
                    # junctable NEMids are dimly colored
                    self.fill = (244, 244, 244)
                    self.outline = dim_color(strand.styles.color.value, 0.5), 0.3
                else:
                    # non-junctable NEMids are normally colored
                    self.fill = dim_color(strand.styles.color.value, 0.9)

                    # If strand color is light use dark outline else use a light outline
                    self.outline = (
                        ((200, 200, 200), 0.65)
                        if (sum(strand.styles.color.value) < (255 * 3) / 2)
                        else ((0, 0, 0), 0.5)
                    )

            # Enlarge the point if the strands strand exists and is highlighted
            if strand is not None and strand.styles.highlighted:
                self.size += 5


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
        strand: The strand that this point belongs to. Can be None.
        linkage: The linkage that this point belongs to. Can be None.
        domain: The domain this point belongs to.
        styles: The styles of the point.
        uuid (str): The uuid of the point. This is automatically generated post init.

    Methods:
        matching: Obtain the matching point on the other helix of the same domain.
        x_coord_from_angle: Obtain the x coord of the point from the angle.
        position: Obtain the position of the point as a tuple.
        is_endpoint: Return whether the point is an endpoint in the strand.
        midpoint: Obtain the midpoint between this point and a different point.
        overlaps: Return whether the point overlaps with another point.
    """

    # positional attributes
    x_coord: float = None
    z_coord: float = None
    angle: float = None

    # nucleic acid attributes
    direction: int = None
    strand: Type["Strand"] = field(default=None, repr=False)
    linkage: Type["Linkage"] = None
    domain: Type["Domain"] = None

    # plotting attributes
    styles: PointStyles = field(default=None, repr=False)

    uuid: str = field(default_factory=lambda: str(uuid1()))

    def __post_init__(self):
        """
        Post-init function.

        1) Modulo the angle to be between 0 and 360 degrees.
        2) Ensure that the direction is either UP or DOWN.
        3) Compute the x coord from the angle if the x coord is not provided.
        4) Set the styles of the point.
        5) Generate a UUID for the point.
        """
        # Modulo the angle to be between 0 and 360 degrees
        if self.angle is not None:
            self.angle %= 360

        # Compute the x coord from the angle if the x coord is not provided
        if self.x_coord is None and self.angle is not None and self.domain is not None:
            self.x_coord = self.x_coord_from_angle(self.angle, self.domain)

        # Ensure that the direction is either UP or DOWN
        if self.direction not in (UP, DOWN, None):
            raise ValueError("Direction must be UP or DOWN.")

        # Set the styles
        if self.styles is not None:
            self.styles.point = self
        else:
            self.styles = PointStyles(point=self)

        self.styles.reset()

    def overlaps(self, point: Type["Point"], width=None) -> bool:
        """
        Return whether the point overlaps with another point.

        Args:
            point: The point to check for overlap with.
            width: The width of the strands container. This is generally equal to the
                number of double helices in the strands container. If not provided,
                the width is extracted from the points' strand's strands container.

        Returns:
            True: If the point is within setting.junction_threshold distance of the
                other point or, if the point has a parent strand, and the parent
                strand has a parent Strands container, then if one point is on the
                left side of the Strands container and the other is on the right if
                the z coords are within the junction threshold.
            False: Otherwise.
        """
        # Return True if the points are within junction_threshold distance of
        # each other
        if dist(self.position(), point.position()) < settings.junction_threshold:
            return True
        # If there is a parent strands container for both the points and it is the same
        elif (self.x_coord == 0 or point.x_coord == 0) and (
            width is not None
            or (
                self.strand is not None
                and point.strand is not None
                and self.strand.strands is not None
                and point.strand.strands is not None
                and self.strand.strands is point.strand.strands
            )
        ):
            width = width or len(self.strand.strands.double_helices)
            right_side_point = point if self.x_coord == 0 else self
            if (
                abs(right_side_point.x_coord - width) < settings.junction_threshold
            ) and (abs(point.z_coord - self.z_coord) < settings.junction_threshold):
                return True

    def midpoint(self, point: "Point") -> Tuple[float, float]:
        """
        Obtain the midpoint location between this point and a different point.

        Args:
            point: The point to find the midpoint with.

        Returns:
            The midpoint location as a tuple.
        """
        return (self.x_coord + point.x_coord) / 2, (self.z_coord + point.z_coord) / 2

    def matching(self) -> Type["Point"] | None:
        """
        Obtain the matching point.

        The matching point is determined based off of the strands strand's .double_helices.
        .double_helices is a formatted list of domains' up and down strands. We will use this
        to determine the matching point on the other strand of ours.

        Returns:
            Point: The matching point.
            None: There is no matching point. This is the case for closed strands,
                or for when there is no double_helices within the strands's Strands object.
        """
        # our domain's strands is a subunit; our domain's subunit's strands is a
        # Domains object we need access to this Domains object in order to locate the
        # matching point
        if (
            self.strand.closed
            or self.strand is None
            or self.strand.strands.double_helices is None
        ):
            return None
        else:
            # create a reference to the strands double_helices
            strands: List[Tuple["Strand", "Strand"]]
            strands = self.strand.strands.double_helices

            # obtain the helix that we are contained in
            our_helix: "Strand" = strands[self.domain.index][self.direction]
            # determine our index in our helix
            our_index = our_helix.index(self)

            # obtain the other helix of our domain
            other_helix: "Strand" = strands[self.domain.index][inverse(self.direction)]
            # since the other strand in our domain is going in the other direction,
            # we reverse the other helix
            other_helix: Tuple[Point] = tuple(reversed(other_helix.items))

            # obtain the matching point
            try:
                matching: Point = other_helix[our_index]
            except IndexError:
                return None

            if isinstance(matching, type(self)):
                return matching
            else:
                return None

    def surf_strand(self, dist) -> Type["Point"] | None:
        """
        Obtain the point on the point's strand that is dist away from this point.

        Parameters:
            dist: The distance away from this point to obtain the point.

        Returns:
            Point: The point that is dist away from this point.
            None: There is no point that is dist away from this point.
        """
        # obtain the index of this point
        index = self.strand.index(self)

        # obtain the point that is dist away from this point
        return self.strand.items[index + dist]

    def is_endpoint(self, of_its_type=False) -> bool:
        """
        Return whether the point is either the last or the first item in its strand.

        By default, this method returns whether the point is the last or the first item
        in its strand. If of_its_type is True then this method returns whether the point
        is the last or the first item of its type in its strand.

        Args:
            of_its_type: Whether to only consider the point an endpoint if it is
                the last/first of its type (i.e. a Nucleoside or a NEMid). This
                method obtains a list of all the points of the specific subtype that
                this point is, and then sees if this point is the first or last item
                in that list.

        Returns:
            bool: Whether the point is an endpoint in the strand. If the point's strand
                is None then this method returns False.
        """
        if self.strand is None:
            return False

        if of_its_type:
            items = self.strand.items.by_type(type(self))
            return self == items[0] or self == items[-1]
        else:
            return self == self.strand.items[0] or self == self.strand.items[-1]

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
        Obtain the index of this domain in its respective strands strand.

        Returns:
            int: The index of this domain in its respective strands strand.
            None: This point has no strands strand.

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

        This function merely changes the formatting of the x and z coords to be a zipped
        tuple.
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


def to_df(points: Iterable[Point]) -> pd.DataFrame:
    """
    Export an iterable of points to a csv file or pandas dataframe.

    Creates a dataframe that has all the attributes that points possess, including
    the point styles.

    Args:
        points: The points to export.

    Returns:
        pd.DataFrame: A dataframe that has all the points and their attributes.
    """
    # create a dataframe from the points
    data = {
        "uuid": [],
        "data:x_coord": [],
        "data:z_coord": [],
        "data:angle": [],
        "data:domain": [],
        "data:direction": [],
        "style:symbol": [],
        "style:size": [],
        "style:rotation": [],
        "style:fill": [],
        "style:outline": [],
        "style:state": [],
    }
    for point in points:
        data["uuid"].append(point.uuid)
        data["data:x_coord"].append(point.x_coord)
        data["data:z_coord"].append(point.z_coord)
        data["data:angle"].append(point.angle)
        data["data:domain"].append(
            point.domain.index if point.domain is not None else None
        )
        data["data:direction"].append("UP" if point.direction == UP else "DOWN")
        data["style:symbol"].append(point.styles.symbol)
        data["style:size"].append(point.styles.size)
        data["style:rotation"].append(point.styles.rotation)
        data["style:fill"].append(rgb_to_hex(point.styles.fill))
        data["style:outline"].append(
            f"{rgb_to_hex(point.styles.outline[0])}, " f"{point.styles.outline[1]}px"
        )
        data["style:state"].append(point.styles.state)

    return pd.DataFrame(data)
