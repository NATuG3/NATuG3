from collections import deque
from dataclasses import dataclass
from typing import Deque, Literal, Tuple, Iterable, List
from uuid import uuid1

import numpy as np
import pandas as pd

from constants.directions import UP, DOWN
from structures.points import Nucleoside
from ui.plotters.utils import chaikins_corner_cutting


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
        count: The number of nucleosides that the linkage starts with.
        items: A list of all the points in the linkage.
        styles: A list of styles to apply to the linkage when it is plotted.
        strand: The strand that the linkage is a part of.
        sequence: The bases of the nucleosides, as a list of strings of capital letters.
        plot_points: The points to plot the linkage with. This is a tuple of three
            tuples, where the first is the position of the lefter Nucleoside from
            initialisation, the second is the position of the righter Nucleoside from
            initialisation, and the third is the average of the two, with a boost in its
            z coord.
        inflection: Whether the linkage is bent upwards or downwards when plotted.
        uuid (str): The unique identifier of the linkage. Automatically generated post
        init.

    Methods:
        trim: Trim the linkage to a certain length.
        generate: Generate additional Nucleoside objects, and add them to the linkage.
    """

    def __init__(
        self,
        coord_one: Tuple[float, float],
        coord_two: Tuple[float, float],
        inflection: Literal[UP, DOWN],  # type: ignore
        strand: "Strand" = None,  # type: ignore
        count=6,
    ):
        self.inflection: inflection
        self.styles = LinkageStyles()
        self.strand = strand
        self.items = [Nucleoside() for _ in range(count)]

        # Convert the items to a deque if they are not already.
        self._initial_item_coordinates = tuple(item.position() for item in self.items)

        # Ensure all the items are nucleosides
        for item in self.items:
            if not isinstance(item, Nucleoside):
                raise TypeError("All items in a linkage must be nucleosides.")

        # Assign this linkage to the nucleosides.
        for item in self.items:
            item.linkage = self

        # If the midpoint is lower than both of the other points, then the inflection
        # is down.
        midpoint = list(np.mean([np.array(coord_one), np.array(coord_two)], axis=0))
        midpoint[1] += 0.2 if inflection == UP else -0.2
        self.plot_points = [coord_one, midpoint, coord_two]
        self.plot_points = chaikins_corner_cutting(self.plot_points, refinements=4)

        # Set the uuid of the linkage.
        self.uuid = str(uuid1())

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


def export(linkages: Iterable[Linkage], filename: str | None):
    """
    Export an iterable of linkages to a csv file or a pandas dataframe.

    All the items (nucleosides) within the linkage are compressed into a string
    sequence, where each letter is the base of a given nucleoside, and nucleosides
    with None bases are represented with an "X."

    Args:
        linkages: The linkages to export.
        filename: The name of the file to export to. If this is None, then a pandas
            dataframe will be returned instead.
    """
    data = {
        "uuid": [],
        "data:sequence": [],
        "data:inflection": [],
        "data:plot_points": [],
        "data:strand": [],
        "styles:color": [],
        "styles:thickness": [],
    }

    for linkage in linkages:
        data["uuid"].append(linkage.uuid)
        data["data:sequence"].append("".join(map(str, linkage.sequence)))
        data["data:inflection"].append(linkage.inflection)
        data["data:plot_points"].append(linkage.plot_points)
        data["data:strand"].append(linkage.strand.uuid if linkage.strand else None)
        data["styles:color"].append(linkage.styles.color)
        data["styles:thickness"].append(linkage.styles.thickness)

    data = pd.DataFrame(data)

    return data if filename is None else data.to_csv(filename, index=False)
