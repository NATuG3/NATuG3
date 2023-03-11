import itertools
import random
from collections import deque
from copy import deepcopy, copy
from dataclasses import dataclass, field
from typing import Tuple, Iterable, List, Type, Set
from uuid import uuid1

import numpy as np
import pandas as pd

from constants.bases import DNA
from constants.directions import *
from structures.points import NEMid, Nucleoside
from structures.points.point import Point
from structures.profiles import NucleicAcidProfile
from structures.strands.linkage import Linkage
from structures.strands.utils import shuffled
from structures.utils import converge_point_data
from utils import rgb_to_hex


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
        for point in self.strand.items.by_type(Point):
            point.styles.size += 5

    def reset(self):
        """Reset the strand to its default state."""
        if self.highlighted:
            self.highlighted = False
            for point in self.strand.items.by_type(Point):
                point.styles.size -= 5


class StrandItems(deque):
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

    def __getitem__(self, index_or_slice: int | slice) -> object:
        if isinstance(index_or_slice, slice):
            if index_or_slice.step < 0:
                iter_on = reversed(self)
            else:
                iter_on = self
            return itertools.islice(
                iter_on,
                index_or_slice.start,
                index_or_slice.stop,
                abs(index_or_slice.step),
            )
        return super().__getitem__(index_or_slice)

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
        return split

    def unpacked(self) -> List[Point]:
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
        return unpacked

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
        cross_screen: Whether this strand wraps across the screen.
        direction: Whether this is an up or down helix. This is only useful for when
            the strand represents a helix.
        strands: The container that this strand is in. Can be None. Is automatically
            set when the strand is added to a Strands container.
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
        interdomain(): Whether there are items of differing domains in the strand.
        split(index or NEMid): Split the strand into two strands.
        index(item): Determine the index of an item.
        sliced(from, to): Return self.NEMids as a list.
        clear_sequence(overwrite): Clear the sequence of the strand.
        randomize_sequence(overwrite): Randomize the sequence of the strand.
        startswith(point): Determine whether the strand starts with a point.
        endswith(point): Determine whether the strand ends with a point.
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
        uuid: str = None,
    ):
        self.name = name
        self.uuid = uuid or str(uuid1())
        self.items = StrandItems() if items is None else StrandItems(items)
        self.closed = closed
        self.styles = styles or StrandStyles(self)
        self.nucleic_acid_profile = (
            NucleicAcidProfile()
            if nucleic_acid_profile is None
            else nucleic_acid_profile
        )
        self.direction = direction
        self.strands = strands

    def __post_init__(self):
        self.items = StrandItems(self.items)

        for item in self.items:
            item.strand = self

        if self.styles.strand is None:
            self.styles.strand = self

        self.uuid = str(uuid1())

    def __len__(self) -> int:
        """Obtain number of items in strand."""
        return len(self.items)

    def __contains__(self, item) -> bool:
        """Determine whether item is in strand."""
        return item in self.items

    def __getitem__(self, item):
        """Obtain an item from the strand."""
        return self.items[item]

    def __setitem__(self, key, value):
        """Set an item in the strand."""
        self.items[key] = value

    def __iter__(self):
        """Iterate over the strand."""
        return iter(self.items)

    def __deepcopy__(self, memodict={}):
        """Deepcopy the strand."""
        copied = Strand(
            items=deepcopy(self.items, memodict),
            name=self.name,
            closed=self.closed,
            nucleic_acid_profile=self.nucleic_acid_profile,
        )
        copied.styles = copy(self.styles)
        return copied

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

    def trim(self, count: int):
        """
        Remove <count> number of items from the strand.

        Removes from the right side of the strand if count is positive, and from the
        left side of the strand if count is negative.

        Args:
            count: The number of items to remove.
        """
        if count > 0:
            for i in range(count):
                self.items.pop().strand = None
        else:
            for i in range(abs(count)):
                self.items.popleft().strand = None

    def generate(self, count: int, domain: "Domain" = None) -> None:
        """
        Generate additional NEMids and Nucleosides for the strand.

        If a negative count is given, then NEMids and Nucleosides are generated for
        and appended to the left side of the strand. Otherwise, they are generated for
        and appended to the right side of the strand.

        Args:
            count: The number of additional NEMids to generate. Nucleosides are
                generated automatically, this is specifically an integer number of
                NEMids.
            domain: The domain to use for x coord generation in the NEMid generation
                process. If this is None the domain of the right most NEMid is used
                by default if the count is positive, and the domain of the left most
                NEMid is used by default if the count is negative.

        Raises:
            ValueError: If the strand is empty we cannot generate additional NEMids.
        """
        if self.empty:
            raise ValueError("Cannot generate for an empty strand.")

        # Compute variables dependent on direction. Edge_NEMid == rightmost or
        # leftmost NEMid based off of the direction that we're generating NEMids in.
        # Modifier == whether we are increasing or decreasing angles/z-coords as we
        # progress. Takes the form of -1 or 1 so that we can multiply it by the
        # changes.
        if count > 0:
            # If we're generating to the right, the edge NEMid is the rightmost NEMid.
            edge_item = self.items[-1]
            modifier = 1
        elif count < 0:
            # If we're generating to the left, the edge item is the leftmost item.
            edge_item = self.items[0]
            modifier = -1
        else:
            # If count == 0, then we don't need to do anything.
            return

        # If they do not pass a Domain object, use the domain of the right most NEMid
        domain = domain if domain is not None else edge_item.domain

        # Create easy referneces for various nucleic acid setting attributes. This is to
        # make the code more readable.
        theta_b = self.nucleic_acid_profile.theta_b
        Z_b = self.nucleic_acid_profile.Z_b

        # Obtain preliminary data
        initial_angle = edge_item.angle + ((theta_b / 2) * modifier)
        initial_z_coord = edge_item.z_coord + ((Z_b / 2) * modifier)
        final_angle = initial_angle + ((count + 3) * (theta_b * modifier))
        final_z_coord = initial_z_coord + ((count + 3) * (Z_b * modifier))

        # Generate the angles for the points
        angles = np.arange(
            initial_angle,  # when to start generating angles
            final_angle,  # when to stop generating angles
            modifier * (theta_b / 2),  # the amount to step by for each angle
        )

        # Generate additional x coordinates.
        x_coords = [Point.x_coord_from_angle(angle, domain) for angle in angles]
        x_coords = np.array(x_coords)

        # Generate the z coords for the points.
        z_coords = np.arange(
            initial_z_coord,  # when to start generating z coords
            final_z_coord,  # when to stop generating z coords
            modifier * (Z_b / 2),  # the amount to step by for each z coord
        )

        # Ensure that all the items are the same length
        greatest_count = min(
            (
                len(angles),
                len(x_coords),
                len(z_coords),
            )
        )
        angles = angles[:greatest_count]
        x_coords = x_coords[:greatest_count]
        z_coords = z_coords[:greatest_count]

        # Converge the newly generated data and add it to the strand
        new_items = converge_point_data(
            angles,
            x_coords,
            z_coords,
            initial_type=NEMid if isinstance(edge_item, Nucleoside) else Nucleoside,
            break_at=abs(count),
        )

        # Assign domains for all items
        for item in new_items:
            item.domain = domain
            item.direction = edge_item.direction

        if count < 0:
            self.leftextend(new_items)
        else:  # direction == RIGHT:
            self.extend(new_items)

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

    @property
    def sequence(self):
        return [
            nucleoside.base
            for nucleoside in StrandItems(self.items.unpacked()).by_type(Nucleoside)
        ]

    @sequence.setter
    def sequence(self, new_sequence: List[str]):
        nucleosides: List[Nucleoside] = StrandItems(self.items.unpacked()).by_type(
            Nucleoside
        )
        # type: ignore

        if len(new_sequence) == len(self.sequence):
            for index, base in enumerate(new_sequence):
                our_nucleoside = nucleosides[index]
                our_nucleoside.base = base

                matching_nucleoside = our_nucleoside.matching
                if matching_nucleoside is not None:
                    matching_nucleoside.complement = our_nucleoside.base
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
        print(StrandItems(self.items.unpacked()).by_type(Nucleoside))
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

        Uses self.random_sequence() to compute the random sequence

        Args:
            overwrite: Whether to overwrite the current sequence or not. If overwrite
                is False then all unset nucleosides (ones which are None) will be set
                to a random nucleoside. If overwrite is True then all nucleosides
                will be set to a random nucleoside.
        """
        for nucleoside in self.items.by_type(Nucleoside):
            if overwrite or nucleoside.base is None:
                nucleoside.base = random.choice(DNA)
                if nucleoside.matching is not None:
                    nucleoside.matching.base = nucleoside.complement

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

    def cross_screen(self) -> bool:
        """
        Whether the strand wraps across the screen.

        This is determined by checking to see if any active junctions are cross screen.

        Returns:
            True if the strand wraps across the screen, False otherwise.
        """
        junctions = filter(lambda NEMid_: NEMid_.junction, self.items.by_type(NEMid))
        for junction in junctions:
            if abs(junction.x_coord - junction.juncmate.x_coord) > 1:
                return True
        return False

    def interdomain(self) -> bool:
        """Whether all the items in this strand belong to the same domain."""
        try:
            checker = self.items.by_type(Point)[0].domain
            for item in self.items.by_type(Point):
                if isinstance(item, Point):
                    if item.domain is not checker:
                        return True
        except IndexError:
            return False

        return False

    def size(self) -> Tuple[float, float]:
        """
        The overall size of the strand in nanometers.

        Returns:
            Tuple(width, height): The strand size.
        """
        width = max([item.x_coord for item in self.items]) - min(
            [item.x_coord for item in self.items]
        )
        height = max([item.z_coord for item in self.items]) - min(
            [item.z_coord for item in self.items]
        )
        return width, height


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
