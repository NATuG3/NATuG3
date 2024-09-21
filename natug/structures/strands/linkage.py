from dataclasses import InitVar, dataclass
from typing import Iterable, List, Literal, Tuple
from uuid import uuid1

import numpy as np
import pandas as pd

from natug import settings
from natug.constants.directions import DOWN, UP
from natug.structures.points import Nucleoside
from natug.ui.plotters.utils import chaikins_corner_cutting
from natug.utils import rgb_to_hex


@dataclass
class LinkageStyles:
    """
    A class to hold the styles for linkages.

    Attributes:
        linkage: The linkage that the styles are for.
        color: The color of the linkage as RGB. In the form (R, G, B).
        thickness: The width of the linkage. This is in pixels.
    """

    linkage: "Linkage" = None
    color: Tuple[int, int, int] = None
    thickness: int = None
    init_reset: InitVar[bool] = True

    def __post_init__(self, init_reset: bool):
        if init_reset:
            self.reset()

    def reset(self):
        """
        Set the default styles for linkages.

        The color is light pink by default; the thickness is 3px.
        """
        if self.linkage.strand is not None and self.linkage.strand.interdomain():
            self.color = settings.colors["linkages"]["color"]
        else:
            self.color = settings.colors["linkages"]["grey"]

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
        items: Iterable[Nucleoside] = None,
        count: int = 6,
        uuid: str = None,
        styles: LinkageStyles = None,
    ):
        self.inflection = inflection
        self.strand = strand
        self.styles = styles or LinkageStyles(linkage=self)
        self.items = items or [Nucleoside() for _ in range(count)]

        # Convert the items to a list if they are not already.
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
        basic_plot_points = [coord_one, midpoint, coord_two]
        self.plot_points = chaikins_corner_cutting(basic_plot_points, refinements=3)

        # Set the uuid of the linkage.
        self.uuid = uuid or str(uuid1())

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
            self.items = [Nucleoside(linkage=self) for _ in range(-length)] + self.items
        else:
            self.items += [Nucleoside(linkage=self) for _ in range(length)]

    def trim(self, length: int):
        """
        Trim the linkage to a certain length.

        Args:
            length: The length to trim the linkage to. If negative, trim the linkage
                to the left. If positive, trim the linkage to the right.
        """
        if length < 0:
            self.items = list(self.items)[:length]
        else:
            self.items = list(self.items)[length:]

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

    def position(self):
        return self.plot_points[1][0], self.plot_points[1][1]

    def append(self, item: Nucleoside):
        """Append a point to the linkage."""
        self.items.append(item)

    def extend(self, items: List[Nucleoside]):
        """Extend the linkage with a list of points."""
        self.items.extend(items)


def to_df(linkages: Iterable[Linkage]):
    """
    Export an iterable of linkages to a pandas dataframe.

    All the items (nucleosides) within the linkage are compressed into a string
    sequence, where each letter is the base of a given nucleoside, and nucleosides
    with None bases are represented with an "X."

    Args:
        linkages: The linkages to export.
    """
    data = {
        "uuid": [],
        "data:sequence": [],
        "data:inflection": [],
        "data:coord_one": [],
        "data:coord_two": [],
        "data:strand": [],
        "style:color": [],
        "style:thickness": [],
    }

    for linkage in linkages:
        sequence = ""
        for nucleoside in linkage:
            sequence += nucleoside.base or "X"

        data["uuid"].append(linkage.uuid)
        data["data:sequence"].append(sequence)
        data["data:inflection"].append(linkage.inflection)
        data["data:coord_one"].append(", ".join(map(str, linkage.plot_points[0])))
        data["data:coord_two"].append(", ".join(map(str, linkage.plot_points[-1])))
        data["data:strand"].append(linkage.strand.uuid if linkage.strand else None)
        data["style:color"].append(rgb_to_hex(linkage.styles.color))
        data["style:thickness"].append(linkage.styles.thickness)

    return pd.DataFrame(data)
