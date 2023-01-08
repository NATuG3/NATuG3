from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Literal, Tuple, Iterable
import matplotlib.path as mpath

from constants.directions import UP, DOWN
from structures.points import NEMid, Nucleoside
from structures.points.point import Point


@dataclass
class LinkageStyles:
    """
    A class to hold the styles for linkages.

    Attributes:
        color: The color of the linkage as RGB. In the form (R, G, B).
        thickness: The width of the linkage. This is in pixels.
    """

    color: Tuple[int, int, int] = None
    thickness: int = None

    def __post_init__(self):
        self.reset()

    def reset(self):
        """
        Set the default styles for linkages.

        The color is light pink by default; the thickness is 3px.
        """
        self.color = (255, 192, 203)
        self.thickness = 3


@dataclass
class Linkage:
    """
    A single stranded region between the ends of two strands.

    Attributes:
        items: A list of all the points in the linkage.
        direction: The direction to bend the linkage when the linkage is plotted.
            Note that the linkage is bent and curved when it is plotted.
        styles: A list of styles to apply to the linkage when it is plotted.
        strand: The strand that the linkage is a part of.
    """

    items: Iterable[Point] = field(default_factory=deque)
    direction: Literal[UP, DOWN] = UP
    styles: LinkageStyles = field(default_factory=LinkageStyles)
    strand: "Strand" = None

    domain = None

    def __post_init__(self):
        self.items = deque(self.items)

    def __setitem__(self, key, value):
        self.items[key] = value

    def __getitem__(self, item):
        return self.items[item]

    def __delitem__(self, key):
        del self.items[key]

    def append(self, item: Point):
        """Append a point to the linkage."""
        self.items.append(item)

    def leftappend(self, item: Point):
        """Append a point to the left of the linkage."""
        self.items.appendleft(item)

    def extend(self, items: Deque[Point]):
        """Extend the linkage with a list of points."""
        self.items.extend(items)

    def leftextend(self, items: Deque[Point]):
        """Extend the linkage with a list of points to the left."""
        self.items.extendleft(items)

    def plotting_coords(self, resolution: int):
        """
        Obtain a list of points for plotting of the linkage.

        A linkage's individual points are not plotted. Rather, the slightly curved
        arc is generally plotted in a thin stroke to indicate the existence of a
        linkage.

        To determine the linkage's plotting coordinates, we look at the first point
        in the linkage, the middlemost x coord point in the linkage, and the right
        most point in the linkage. Then we move the middlemost x coord point upwards
        slightly, and create a quadratic bezier curve between the three points.

        Args:
            resolution: The resolution of the plot. This is the number of times the
                plotting coordinates are calculated. The higher the resolution, the
                smoother the curve.

        Returns:
            A list of plotting coordinates. Each coordinate is a tuple of the form
            (x, y).
        """
        # get the first point in the linkage
        first_point = self.items[0].x_coord, self.items[0].z_coord

        # obtain the midpoint. This is mean x coord, mean y coord for all points
        middle_point = [
            sum([item.x_coord for item in self.items]) / len(self.items),
            sum([item.z_coord for item in self.items]) / len(self.items),
        ]
        middle_point[0] += 0.2

        # get the last point in the linkage
        last_point = self.items[-1].x_coord, self.items[-1].z_coord

        path = mpath.Path(first_point, middle_point, last_point)

        # return the plotting coordinates. this creates a Bézier curve with the three
        # points
        return path.interpolated(resolution).vertices

    def NEMids(self):
        """Return all NEMids in the linkage."""
        return [item for item in self.items if isinstance(item, NEMid)]

    def nucleosides(self):
        """Return all nucleosides in the linkage."""
        return [item for item in self.items if isinstance(item, Nucleoside)]
