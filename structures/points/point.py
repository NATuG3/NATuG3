import logging
from dataclasses import dataclass
from typing import Tuple, Type, List

import settings
from constants.directions import DOWN, UP
from utils import inverse

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
            isn't a default symbol (is not in _all_symbols). This is in degrees.
        fill: The color of the Point. Tuple of (r, g, b) values.
        outline: The color of the outline of the Point. Tuple of (color, width).

    Methods:
        set_defaults: Automatically set the color of the Point.
        highlight: Highlight the point.
        select: Select the point.
    """

    point: "Point" = None
    symbol: str = "o"
    size: int = 10
    rotation: float = 0
    fill: Tuple[int, int, int] = (0, 0, 0)
    outline: Tuple[Tuple[int, int, int], float] = (0, 0, 0), 0.5

    _all_symbols = ("o", "t", "t1", "t2", "t3", "s", "p", "h", "star", "+", "d", "x")

    def symbol_is_custom(self):
        """Return whether the symbol is a custom symbol."""
        return self.symbol not in self._all_symbols

    def highlight(self):
        """Highlight the point."""
        from ui.plotters.utils import dim_color

        self.fill = settings.colors["highlighted"]
        self.size = 18
        self.rotation = 0
        self.outline = dim_color(self.fill, 0.7), 1

    def select(self):
        """Select the point."""
        from ui.plotters.utils import dim_color

        self.fill = settings.colors["selected"]
        self.size = 18
        self.rotation = 0
        self.outline = dim_color(self.fill, 0.7), 1

    def reset(self):
        """
        Automatically set the color of the Point.

        Raises:
            ValueError: If the point does not have a strand associated with it.
        """
        from structures.points import Nucleoside, NEMid
        from ui.plotters.utils import dim_color

        strand, point = self.point.strand, self.point  # Create easy references

        if self.point.strand is None:
            raise ValueError("Point does not have a strand associated with it.")

        if point.highlighted:
            self.highlight()
        elif point.selected:
            self.select()
        elif isinstance(point, Nucleoside):
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

        # Enlarge the point if the parent strand exists and is highlighted
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
        strand: The strand that this point belongs to.
        domain: The domain this point belongs to.
        matching: Point in same domain on other direction's helix across from this one.
        highlighted: Whether the point is highlighted.
        selected: Whether the point is selected.
        index: Index of the point in respect to its parent strand. None if there is
            no parent strand set.
        symbol_str: The symbol of the point as a string. Automatically determined if
        None.
        symbol_size: The size of the point's symbol in pixels. Automatically determined if
            None.
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
    selected: bool = False
    styles: PointStyles = None

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

        # Set the styles
        if self.styles is not None:
            self.styles.point = self
        else:
            self.styles = PointStyles(point=self)

        # If highlighted, highlight the point
        if self.highlighted:
            self.styles.highlight()

    def matching(self) -> Type["Point"] | None:
        """
        Obtain the matching point.

        The matching point is determined based off of the parent strand's .double_helices.
        .double_helices is a formatted list of domains' up and down strands. We will use this
        to determine the matching point on the other strand of ours.

        Returns:
            Point: The matching point.
            None: There is no matching point. This is the case for closed strands,
                or for when there is no double_helices within the parent's Strands object.
        """
        # our domain's parent is a subunit; our domain's subunit's parent is a
        # Domains object we need access to this Domains object in order to locate the
        # matching point
        if (
            self.strand.closed
            or self.strand is None
            or self.strand.parent.double_helices is None
        ):
            return None
        else:
            # create a reference to the strands double_helices
            strands: List[Tuple["Strand", "Strand"]]
            strands = self.strand.parent.double_helices

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
