import itertools
import logging
import random
from copy import copy, deepcopy
from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Set, Tuple, Type
from uuid import uuid1

import pandas as pd

from natug.constants.bases import DNA
from natug.constants.directions import *
from natug.structures.points import NEMid, Nucleoside
from natug.structures.points.point import Point
from natug.structures.profiles import NucleicAcidProfile
from natug.structures.strands.linkage import Linkage
from natug.structures.strands.utils import shuffled
from natug.utils import rgb_to_hex

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Wrap:
    direction: WRAPS_LEFT_TO_RIGHT | WRAPS_RIGHT_TO_LEFT
    point: Point


@dataclass
class StrandStyle:
    """
    A container for the style of a Point.

    Attributes:
        automatic: Whether the style is automatically determined when
            strands.style() is called.
        value: The value of the specific style.

    Methods:
        as_str: Return the value and automatic-ness as a string.
        from_str: Set the value and automatic-ness from a string.
    """

    automatic: bool = True
    value: str | int = None

    def as_str(self, valuemod=lambda value: value) -> str:
        """
        Return the value and automatic-ness as a string.

        Args:
            valuemod: A function to modify the value before it is returned.

        Returns:
            str: The value and automatic-ness as a string.
        """
        value = valuemod(self.value)
        return f"{value}{', auto' if self.automatic else ''}"

    def from_str(self, string: str, valuemod=lambda value: value) -> None:
        """
        Set the value and automatic-ness from a string.

        Args:
            string: The string to set the value and automatic-ness from.
            valuemod: A function to modify the value before it is set.
        """
        if string[-1] == ", auto":
            self.automatic = True
            self.value = valuemod(string.replace(", auto", ""))
        else:
            self.automatic = False
            self.value = valuemod(string.replace(", auto", ""))

    def __deepcopy__(self, memodict={}):
        return StrandStyle(self.automatic, deepcopy(self.value))


@dataclass
class StrandStyles:
    """
    A container for the styles of a Point.

    Attributes:
        strand: The strand that the styles are for.
        thickness: The thickness of the strand.
        color: The color of the strand.
        highlighted: Whether the strand is highlighted.

    Methods:
        set_defaults: Automatically set the color of the Point.
    """

    strand: "Strand" = None
    thickness: StrandStyle = field(default_factory=StrandStyle)
    color: StrandStyle = field(default_factory=StrandStyle)
    highlighted: bool = False

    def __post_init__(self):
        if self.thickness.value is None:
            self.thickness.value = 3
        if self.color.value is None:
            self.color.value = (255, 192, 203)

    def highlight(self):
        """Highlight the strand."""
        self.highlighted = True
        self.strand.strands.style()

    def reset(self):
        """Reset the strand to its default state."""
        self.highlighted = False
        self.strand.strands.style()

    def __deepcopy__(self, memodict={}):
        return StrandStyles(
            self.strand,
            deepcopy(self.thickness),
            deepcopy(self.color),
            self.highlighted,
        )


class StrandItems(list):
    """
    A container for the items in a Strand.

    This is a subclass of deque with various utility methods.

    Methods:
        NEMids: A list of all the NEMids in the StrandItems.
        nucleosides: A list of all the nucleosides in the StrandItems.
        unpacked: A list of all the items in the StrandItems where all iterables are
            unpacked.
        unpack: Replace all the items in the StrandItems with the unpacked version of
            the StrandItems.
        item_types: A list of all the types of items in the StrandItems.
    """

    def by_type(self, *types) -> "StrandItems":
        """
        Obtain a list of all the items of a specific type.

        Args:
            types: The types of items to obtain. If multiple types are specified, the
                items of the types will be returned. Include types in the
                function call as arguments.
        Returns:
            list: A list of all the items of the specified type.
        """
        return StrandItems((item for item in self if isinstance(item, types)))

    def __add__(self, other):
        new_strand_items = self
        new_strand_items.extend(other)
        return new_strand_items

    def split(self, type_: Type) -> List[List[object]]:
        """
        Split the items into a list of lists. A new list is created whenever an item
        of the specified type is encountered. The items of the specified type are not
        included in the returned lists.

        Args:
            type_: The type of items to split on.

        Returns:
            list: A list of lists of items split on the specified type.
        """
        split = [[]]
        for item in self:
            if isinstance(item, type_):
                split.append([])
            else:
                split[-1].append(item)
        return split[:-1] if split[-1] == [] else split

    def unpacked(self) -> "StrandItems":
        """
        Obtain an unpacked version of the items.

        Return a list of all the contained items, and for each item, if it is an
        iterable, unpack it.

        Returns:
            list: A list of all the items in the StrandItems where all iterables are
            unpacked.
        """
        unpacked = []
        for item in self:
            if isinstance(item, Iterable):
                unpacked.extend(item)
            else:
                unpacked.append(item)
        return StrandItems(unpacked)

    def item_types(self) -> Set[Type]:
        """
        Obtain a list of all the types of items in the StrandItems.

        Returns:
            list: A list of all the types of items in the StrandItems.
        """
        return set([type(item) for item in self])


class Strand:
    """
    A strand of items.

    Attributes:
        name: The user-set name of the strand. This appears when exporting, and is used
            as a title.
        styles: The styles of the strand.
        items: The items in the strand. This is a deque of Points.
        nucleic_acid_profile: The nucleic acid settings used.
        sequence (list): The sequence of the strand.
            This is a list of all the bases of all the nucleosides in the strand.
        closed: Whether the strand is closed. Must be manually set.
        empty: Whether the strand is empty. This is equivalent to len(self) == 0.
        direction: Whether this is an up or down helix. This is only useful for when
            the strand represents a helix.
        strands: The container that this strand is in. Can be None. Is automatically
            set when the strand is added to a Strands container.
        helix: The helix that the strand was generated from. Can be None if the strand
            was not generated from a helix.
        cross_screen: Whether the strand wraps around the screen in the side view plot.
            This is automatically set during plotting with the SideViewPlotter, but can be
            set manually.
        uuid (str): The unique identifier of the strand. This is automatically
            generated.

    Methods:
        append(item): Add an item to the right of the strand.
        appendleft(item): Add an item to the left of the strand.
        extend(items): Extend our items to the right with an iterable's items.
        extendleft(items): Extend our items to the left with an iterable's items.
        reverse(): Reverse the order of the items in the strand.
        generate(count, domain): Generate additional NEMids and Nucleosides to the
            right side of the strand.
        generateleft(count, domain): Generate additional NEMids and Nucleosides to
            left side of the strand.
        up_strand(): Whether all items in this strand are upwards pointing.
        down_strand(): Whether all items in this strand are downwards pointing.
        NEMids(): Obtain all NEMids in the strand, only.
        nucleosides(): Obtain all nucleosides in the strand, only.
        junctables(): Obtain all junctable NEMids in the strand, only.
        interdomain(): Whether there are items of differing domains in the strand.
        split(index or NEMid): Split the strand into two strands.
        index(item): Determine the index of an item.
        sliced(from, to): Return self.NEMids as a list.
        clear_sequence(overwrite): Clear the sequence of the strand.
        randomize_sequence(overwrite): Randomize the sequence of the strand.
        startswith(point): Determine whether the strand starts with a point.
        endswith(point): Determine whether the strand ends with a point.
        has_linkage(): Determine whether the strand has any linkages.
        clear(): Clear the strand.
    """

    def __init__(
        self,
        items: Iterable[Point] = None,
        name: str = "Strand",
        closed: bool = False,
        styles: StrandStyles = None,
        nucleic_acid_profile: NucleicAcidProfile = None,
        direction=None,
        strands=None,
        helix=None,
        cross_screen=None,
        uuid: str = None,
    ):
        self.name = name
        self.uuid = uuid or str(uuid1())
        self.items = StrandItems() if items is None else StrandItems(items)
        self.closed = closed
        self.helix = helix
        self.styles = styles or StrandStyles(self)
        self.nucleic_acid_profile = (
            NucleicAcidProfile()
            if nucleic_acid_profile is None
            else nucleic_acid_profile
        )
        self.direction = direction
        self.strands = strands
        self.cross_screen = cross_screen

    def __post_init__(self):
        self.items = StrandItems(self.items)

        for item in self.items:
            item.strand = self

        if self.styles.strand is None:
            self.styles.strand = self

        self.uuid = str(uuid1())

    def __len__(self) -> int:
        """Obtain number of items in strand."""
        return len(self.items.unpacked())

    def __contains__(self, item) -> bool:
        """Determine whether item is in strand."""
        return item in self.items

    def __getitem__(self, index_or_slice):
        """Obtain an item from the strand."""
        return self.items[index_or_slice]

    def __setitem__(self, key, value):
        """Set an item in the strand."""
        self.items[key] = value

    def __iter__(self):
        """Iterate over the strand."""
        return iter(self.items)

    def __deepcopy__(self, memodict={}):
        """Deepcopy the strand."""
        new_strand = Strand(
            items=copy(self.items),
            name=self.name,
            closed=self.closed,
            styles=deepcopy(self.styles),
            nucleic_acid_profile=self.nucleic_acid_profile,
            strands=self.strands,
        )
        new_strand.styles.strand = new_strand
        for point in new_strand:
            point.styles = copy(point.styles)
        return new_strand

    def clear(self) -> None:
        """Clear the strand."""
        self.items.clear()

    def reverse(self) -> None:
        """Reverse the order of the items in the strand."""
        self.items.reverse()

    def split(self, index_or_item) -> Tuple["Strand", "Strand"]:
        """
        Split the strand into two strands.

        Creates two strand objects with the same attributes as this strand, but with
        different items. The first strand will have all items up to and including the
        index provided; the second strand will have all items after that index.

        Args:
            index_or_item: The index of the item to split at or an item within the
                strand.

        Returns:
            A tuple of two strands.

        Notes:
            The item at the index provided will not be included in either strand.
        """
        # Obtain the index of the item to split at.
        index = (
            self.index(index_or_item)
            if isinstance(index_or_item, Point)
            else index_or_item
        )

        # Create two new strands (these are copies of this strand).
        attrs = {
            "nucleic_acid_profile": self.nucleic_acid_profile,
            "closed": self.closed,
        }
        strand1, strand2 = Strand(**attrs), Strand(**attrs)

        # Set both the new strands to be open (since they were split)
        strand1.closed = strand2.closed = False

        # Set the items of the new strands
        strand1.items = self.sliced(0, index)
        strand2.items = self.sliced(index + 1, None)

        # Update the items' parents (.strand)
        for item in strand1.items:
            item.strand = strand1
        for item in strand2.items:
            item.strand = strand2

        self.strands.style()

        return strand1, strand2

    def matching_items(self, other: "Strand") -> bool:
        """
        Determine whether this strand has items that match a different strand.

        This method first checks if the length of the strands are equal, and then
        recursively checks each item against the item of the same index in the other
        strand (by zipping). If the two items are of different types or do not have all
        the same attributes, then False is returned. If all items match, we return True.

        Args:
            other: The other strand to compare to.

        Returns:
            Whether the strands have matching items.
        """
        # If the lengths are different, then the strands are not matching.
        if len(self) != len(other):
            return False

        # Check each item in the strand against the item of the same index in the other.
        for item, other_item in zip(self.items, other.items):
            # If the items are not the same type, they cannot match.
            if type(item) != type(other_item):
                return False
            # Check each attribute of item against other_item's
            for attr in item.__dataclass_fields__:
                if getattr(item, attr) != getattr(other_item, attr):
                    return False

        # If we get here, then all items match.
        return True

    def remove(self, item: Point) -> None:
        """Remove an item from the strand."""
        self.items.remove(item)
        item.strand = None

    def append(self, item: Point | Linkage) -> None:
        """Add an item to the right of the strand."""
        item.strand = self
        self.items.append(item)

    def appendleft(self, item: Point | Linkage):
        """
        Add an item to the left of the strand.

        Args:
            item: The item to add.
        """
        item.strand = self
        self.items.appendleft(item)

    def extend(self, items: Iterable[Point | Linkage]) -> None:
        """
        Extend our items to the right with an iterable's items.

        Args:
            items: The iterable to extend with.
        """
        for item in items:
            item.strand = self
        self.items.extend(items)

    def leftextend(self, items: Iterable[Point | Linkage]) -> None:
        """
        Extend our items to the left with an iterable's items.

        Args:
            items: The iterable to extend with.
        """
        for item in items:
            item.strand = self
        self.items.extendleft(items)

    def NEMids(self) -> List[NEMid]:
        """
        Obtain all NEMids in the strand, only.

        Utilizes self.items.by_type(NEMid) to obtain the NEMids.

        Returns:
            A list of NEMids in the strand.
        """
        return self.items.by_type(NEMid)

    def nucleosides(self) -> List["Nucleoside"]:
        """
        Obtain all nucleosides in the strand, only.

        Utilizes self.items.by_type(Nucleoside) to obtain the nucleosides.

        Returns:
            A list of nucleosides in the strand.
        """
        return self.items.by_type(Nucleoside)

    def junctables(self) -> Iterator["NEMid"]:
        """
        Obtain all junctable NEMids in the strand, only.

        Utilizes self.NEMids() to obtain the NEMids, and then filters them by their
            junctability.

        Yields:
            NEMids that are junctable.
        """
        return filter(lambda item: item.junctable, self.NEMids())

    def wraps(self, domain_count) -> list[Wrap]:
        """
        Obtain a list of all points that wrap across the screen, going in both directions.
        """
        wraps = []
        for index in range(0, len(self.items) - 1):
            point = self[index % len(self)]
            next_point = self[(index + 1) % len(self)]

            if point.x_coord > domain_count - 1 and next_point.x_coord < 1:
                wraps.append(Wrap(WRAPS_RIGHT_TO_LEFT, point))
                wraps.append(Wrap(WRAPS_LEFT_TO_RIGHT, next_point))
            elif point.x_coord < 1 and next_point.x_coord > domain_count - 1:
                wraps.append(Wrap(WRAPS_LEFT_TO_RIGHT, point))
                wraps.append(Wrap(WRAPS_RIGHT_TO_LEFT, next_point))

        if self.closed:
            if self[0].x_coord < 1 and self[-1].x_coord > domain_count - 1:
                wraps.append(Wrap(WRAPS_LEFT_TO_RIGHT, self[0]))
                wraps.append(Wrap(WRAPS_RIGHT_TO_LEFT, self[-1]))
            elif self[0].x_coord > domain_count - 1 and self[-1].x_coord < 1:
                wraps.append(Wrap(WRAPS_RIGHT_TO_LEFT, self[0]))
                wraps.append(Wrap(WRAPS_LEFT_TO_RIGHT, self[-1]))
        return wraps

    def has_linkage(self) -> bool:
        """Determine whether the strand has any linkages."""
        for item in self.items:
            if isinstance(item, Linkage):
                return True
        return False

    @property
    def sequence(self):
        return [
            nucleoside.base
            for nucleoside in StrandItems(self.items.unpacked()).by_type(Nucleoside)
        ]

    @sequence.setter
    def sequence(self, new_sequence: List[str]):
        logger.debug(f"Setting sequence of %s to %s", self.name, new_sequence)
        nucleosides = self.items.unpacked().by_type(Nucleoside)

        if len(new_sequence) == len(self.sequence):
            for index, base in enumerate(new_sequence):
                our_nucleoside = nucleosides[index]
                our_nucleoside.base = base

                matching_nucleoside = our_nucleoside.matching
                if matching_nucleoside:
                    matching_nucleoside.base = our_nucleoside.complement
        else:
            raise ValueError(
                f"Length of the new sequence ({len(new_sequence)}) must"
                + f"match number of nucleosides in strand ({len(self)})"
            )

    @property
    def complements(self):
        output = [
            nucleoside.matching.base if nucleoside.matching is not None else None
            for nucleoside in StrandItems(self.items.unpacked()).by_type(Nucleoside)
        ]
        return output

    def has_complements(self):
        """
        Return a list of bools that indicate whether the mate of each nucleoside
        is present (True) or not (False).
        """
        return [
            nucleoside.matching is not None
            for nucleoside in StrandItems(self.items.unpacked()).by_type(Nucleoside)
        ]

    @staticmethod
    def random_sequence(length: int) -> List[str]:
        """
        Generate a random sequence of bases.

        Args:
            length: The length of the sequence to generate.

        Returns:
            A list of bases.
        """
        return [random.choice(DNA) for _ in range(length)]

    def randomize_sequence(self, overwrite: bool = False) -> None:
        """
        Randomize the sequence of the strand.

        Args:
            overwrite: Whether to overwrite the current sequence or not. If overwrite
                is False then all unset nucleosides (ones which are None) will be set
                to a random nucleoside. If overwrite is True then all nucleosides
                will be set to a random nucleoside.
        """
        for nucleoside in self.items.unpacked().by_type(Nucleoside):
            if overwrite or nucleoside.base is None:
                nucleoside.base = random.choice(DNA)
                if nucleoside.matching is not None:
                    nucleoside.matching.complement = nucleoside.base

    def clear_sequence(self) -> None:
        """Clear the sequence of the strand."""
        for nucleoside in self.items.by_type(Nucleoside):
            nucleoside.base = None

    def index(self, item) -> int | None:
        """Determine the index of an item."""
        try:
            return self.items.index(item)
        except IndexError:
            return None

    def sliced(self, start: int | None, end: int | None) -> StrandItems:
        """Return self.NEMids as a list."""
        return StrandItems(itertools.islice(self.items, start, end))

    def touching(self, other: "Strand") -> bool:
        """
        Check whether this strand is touching a different strand.

        Args:
            other: The strand potentially touching this one.
        """
        for our_item in shuffled(self.items.by_type(NEMid)):
            for their_item in shuffled(other.items.by_type(NEMid)):
                if our_item.juncmate is their_item:
                    return True
        else:
            # we were not touching
            return False

    @property
    def empty(self) -> bool:
        """Whether this strand is empty."""
        return len(self.items) == 0

    def direction(self) -> int | None:
        """
        Determine the direction of the strand.

        This method utilizes up_strand and down_strand to determine the direction.

        Returns:
            The direction of the strand, or None if the strand does not have one
            finite direction.
        """
        if self.up_strand:
            return UP
        elif self.down_strand:
            return DOWN
        else:
            return None

    def up_strand(self) -> bool:
        """Whether the strand is an up strand."""
        checks = [bool(NEMid_.direction) for NEMid_ in self.items.by_type(NEMid)]
        return all(checks)

    def down_strand(self) -> bool:
        """Whether the strand is a down strand."""
        checks = [(not bool(NEMid_.direction)) for NEMid_ in self.items.by_type(NEMid)]
        return all(checks)

    def interdomain(self) -> bool:
        """Whether all the items in this strand belong to the same domain."""
        from natug.structures.domains import Domain

        try:
            points = self.items.by_type(Point)
            checker = None

            # Find the first domain that shows up in the strand to use as a checker
            for item in points:
                if isinstance(item.domain, Domain):
                    checker = item.domain
                    break

            # Make sure that every other domain is the same as the checker
            for item in points:
                if item.domain != checker and item.domain is not None:
                    return True
        except IndexError:
            return False

        return False

    def y_min(self) -> float:
        """The minimum y-coordinate of the strand."""
        return min([item.z_coord for item in self.items if isinstance(item, Point)])

    def y_max(self) -> float:
        """The maximum y-coordinate of the strand."""
        return max([item.z_coord for item in self.items if isinstance(item, Point)])

    def x_min(self) -> float:
        """The minimum x-coordinate of the strand."""
        return min([item.x_coord for item in self.items if isinstance(item, Point)])

    def x_max(self) -> float:
        """Obtain the maximum x-coordinate of the strand."""
        return max([item.x_coord for item in self.items if isinstance(item, Point)])

    def height(self) -> float:
        """The height of the strand in nanometers."""
        return self.y_max() - self.y_min()

    def width(self) -> float:
        """The width of the strand in nanometers."""
        return self.x_max() - self.x_min()

    def size(self) -> Tuple[float, float]:
        """
        The size of the strand in nanometers.

        Returns:
            The size of the strand.

        Notes:
            The size is defined as the width and height of the strand. If you don't
                need both values, use width() or height() instead.
        """
        return self.width(), self.height()


def to_df(strands: Iterable[Strand]) -> pd.DataFrame:
    """
    Export the strand to a pandas dataframe.

    Arguments:
        strands: All the strands to be exported.

    Returns:
        A pandas dataframe containing data for many strands.
    """
    data = {
        "data:items": [],
        "uuid": [],
        "name": [],
        "data:closed": [],
        "data:nucleic_acid_profile": [],
        "style:thickness": [],
        "style:color": [],
        "style:highlighted": [],
    }

    for strand in strands:
        data["uuid"].append(strand.uuid)
        data["name"].append(strand.name)
        data["data:closed"].append(strand.closed)
        data["data:nucleic_acid_profile"].append(strand.nucleic_acid_profile.uuid)
        data["data:items"].append("; ".join([item.uuid for item in strand.items]))
        data["style:thickness"].append(strand.styles.thickness.as_str())
        data["style:color"].append(strand.styles.color.as_str(valuemod=rgb_to_hex))
        data["style:highlighted"].append(strand.styles.highlighted)

    return pd.DataFrame(data)
