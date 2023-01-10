from collections import deque
from dataclasses import dataclass, field
from functools import cached_property
from typing import Deque, Literal, Tuple, Iterable, ClassVar, List

from constants.directions import UP, DOWN
from structures.points import Nucleoside


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
        styles: A list of styles to apply to the linkage when it is plotted.
        strand: The strand that the linkage is a part of.
        sequence: The bases of the nucleosides, as a list of strings of capital letters.
        plot_points: The points to plot the linkage with. This is a tuple of three
            tuples, where the first is the position of the lefter Nucleoside from
            initialisation, the second is the position of the righter Nucleoside from
            initialisation, and the third is the average of the two, with a boost in its
            z coord.

    Methods:
        trim: Trim the linkage to a certain length.
        generate: Generate additional Nucleoside objects, and add them to the linkage.
    """

    items: Deque[Nucleoside] = field(default_factory=deque)
    inflection: Literal[UP, DOWN] = UP
    styles: LinkageStyles = field(default_factory=LinkageStyles)
    strand: "Strand" = None

    # Items that go into strands must have a domain attribute. This will always be None
    # for linkages.
    domain: ClassVar[None] = None

    def __post_init__(self):
        # Convert the items to a deque if they are not already.
        self.items = deque(self.items)
        self._initial_item_coordinates = tuple(item.position() for item in self.items)

        # Ensure all the items are nucleosides
        for item in self.items:
            if not isinstance(item, Nucleoside):
                raise TypeError("All items in a linkage must be nucleosides.")

        # Clear the angles, x coords, and z coords of all the nucleosides in the
        # linkage. Also, assign this linkage to the nucleosides.
        for item in self.items:
            item.angle = None
            item.x_coord = None
            item.z_coord = None
            item.linkage = self

    @cached_property
    def plot_points(self):
        # Store the plot_points as a tuple of three tuples.
        items_sorted_by_x_coord = sorted(
            self._initial_item_coordinates, key=lambda item: item[0]
        )
        plot_points = (
            items_sorted_by_x_coord[0],
            [
                ((items_sorted_by_x_coord[0][0] + items_sorted_by_x_coord[1][0]) / 2),
                ((items_sorted_by_x_coord[0][1] + items_sorted_by_x_coord[1][1]) / 2),
            ],
            items_sorted_by_x_coord[1],
        )
        # If the midpoint is lower than both of the other points, then the inflection
        # is down.
        if plot_points[0][1] < plot_points[2][1]:
            plot_points[1][1] -= 0.1
        else:
            plot_points[1][1] += 0.1
        return plot_points

    def generate(self, length: int):
        """
        Generate additional nucleosides, and add them to the linkage.

        All the attributes of the generated nucleosides will be None except for
        .linkage, which will be this linkage.

        Args:
            length: The number of nucleosides to generate. If negative, generate
                nucleosides to the left of the linkage. If positive, generate
                nucleosides to the right of the linkage.
        """
        if length < 0:
            for _ in range(-length):
                self.leftappend(Nucleoside(linkage=self))
        else:
            for _ in range(length):
                self.append(Nucleoside(linkage=self))

    def trim(self, length: int):
        """
        Trim the linkage to a certain length.

        Args:
            length: The length to trim the linkage to. If negative, trim the linkage
                to the left. If positive, trim the linkage to the right.
        """
        if length < 0:
            self.items = deque(list(self.items)[:length])
        else:
            self.items = deque(list(self.items)[length:])

    @property
    def sequence(self) -> List[Literal["A", "T", "C", "G"]]:
        """
        Return the sequence of the linkage as a list of strings of bases.
        """
        return [nucleoside.base for nucleoside in self]

    @sequence.setter
    def sequence(self, sequence: Iterable[Literal["A", "T", "C", "G"]]):
        """
        Set the sequence of the linkage.

        Args:
            sequence: The sequence of the linkage as a list of strings of bases.

        Raises:
            ValueError: If the sequence is not the same length as the linkage.
        """
        if len(sequence) != len(self):
            raise ValueError(
                f"Sequence length ({len(sequence)}) does not match the length of the "
                f"linkage ({len(self)})."
            )

        for nucleoside, base in zip(self, sequence):
            nucleoside.base = base

    def __iter__(self):
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __setitem__(self, key, value):
        self.items[key] = value

    def __getitem__(self, item):
        return self.items[item]

    def __delitem__(self, key):
        del self.items[key]

    def append(self, item: Nucleoside):
        """Append a point to the linkage."""
        self.items.append(item)

    def leftappend(self, item: Nucleoside):
        """Append a point to the left of the linkage."""
        self.items.appendleft(item)

    def extend(self, items: Deque[Nucleoside]):
        """Extend the linkage with a list of points."""
        self.items.extend(items)

    def leftextend(self, items: Deque[Nucleoside]):
        """Extend the linkage with a list of points to the left."""
        self.items.extendleft(items)
