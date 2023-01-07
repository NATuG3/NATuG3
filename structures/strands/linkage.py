from collections import deque
from dataclasses import dataclass, field
from typing import Deque, Literal, Tuple

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

    color: Tuple[int, int, int]
    thickness: int

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

    items: Deque[Point] = field(default_factory=deque)
    direction: Literal[UP, DOWN] = UP
    styles: LinkageStyles = field(default_factory=LinkageStyles)
    strand: "Strand" = None

    def unpack(self):
        """
        Unpack the linkage.

        A linkage is a list of points that were between the ends of two strands. To
        remove the linkage we must place the points into the strand at the location
        of the linkage.
        """
        for item in self.items:
            self.strand.insert(self.strand.index(self), item)

    def __getitem__(self, item):
        return self.items[item]

    def __delitem__(self, key):
        del self.items[key]

    def NEMids(self):
        """Return all NEMids in the linkage."""
        return [item for item in self.items if isinstance(item, NEMid)]

    def nucleosides(self):
        """Return all nucleosides in the linkage."""
        return [item for item in self.items if isinstance(item, Nucleoside)]
