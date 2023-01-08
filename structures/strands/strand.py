import itertools
import random
from collections import deque
from dataclasses import dataclass, field
from typing import Tuple, Iterable, Deque, List

import numpy as np

from constants.bases import DNA
from constants.directions import *
from structures.points import NEMid, Nucleoside
from structures.points.point import Point
from structures.profiles import NucleicAcidProfile
from structures.strands.utils import shuffled
from structures.utils import converge_point_data


@dataclass
class StrandStyle:
    """
    A container for the style of a Point.

    Attributes:
        automatic: Whether the style is automatically determined when
            strands.style() is called.
        value: The value of the specific style.
    """

    automatic: bool = True
    value: str | int = None


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
    thickness: float = field(default_factory=StrandStyle)
    color: str = field(default_factory=StrandStyle)
    highlighted: bool = False

    def highlight(self):
        """Highlight the strand."""
        self.highlighted = True
        for point in self.strand:
            point.styles.size += 5

    def reset(self):
        """Reset the strand to its default state."""
        if self.highlighted:
            self.highlighted = False
            for point in self.strand:
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
    """

    def NEMids(self) -> List[NEMid]:
        """
        Obtain a list of all the NEMids in the StrandItems.

        Returns:
            list: A list of all the NEMids in the StrandItems.
        """
        return [item for item in self if isinstance(item, NEMid)]

    def nucleosides(self) -> List[Nucleoside]:
        """
        Obtain a list of all the nucleosides in the StrandItems.

        Returns:
            list: A list of all the nucleosides in the StrandItems.
        """
        return [item for item in self if isinstance(item, Nucleoside)]

    def unpack(self) -> None:
        """
        Unpack the items.

        This utilizes StrandItems.unpacked() to replace the items with the unpacked
        version of the items.
        """
        self.clear()
        self.extend(self.unpacked())

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


@dataclass
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
    """

    name: str = "Strand"
    strands: "Strands" = None

    nucleic_acid_profile: NucleicAcidProfile = field(
        default_factory=NucleicAcidProfile, repr=False
    )
    items: Deque[Point] = field(default_factory=StrandItems)
    closed: bool = False

    styles: StrandStyles = field(default_factory=StrandStyles)

    def __post_init__(self):
        self.items = StrandItems(self.items)
        for item in self.items:
            item.strand = self
        if self.styles.strand == None:
            self.styles.strand = self

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
        strand1, strand2 = Strand(**self.__dict__), Strand(**self.__dict__)

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

    def startswith(self, point: Point) -> bool:
        """
        Determine whether the strand starts with a point.

        Args:
            point: The point to check.

        Returns:
            Whether the strand starts with the point.
        """
        return self.items[0] == point

    def endswith(self, point: Point) -> bool:
        """
        Determine whether the strand ends with a point.

        Args:
            point: The point to check.

        Returns:
            Whether the strand ends with the point.
        """
        return self.items[-1] == point

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
        final_angle = initial_angle + ((count + 1) * (theta_b * modifier))
        final_z_coord = initial_z_coord + ((count + 1) * (Z_b * modifier))

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
            NEMid if isinstance(edge_item, Nucleoside) else Nucleoside,
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

    def append(self, item: Point) -> None:
        """Add an item to the right of the strand."""
        item.strand = self
        self.items.append(item)

    def appendleft(self, item: Point):
        """
        Add an item to the left of the strand.

        Args:
            item: The item to add.
        """
        item.strand = self
        self.items.appendleft(item)

    def extend(self, items: Iterable[Point]) -> None:
        """
        Extend our items to the right with an iterable's items.

        Args:
            items: The iterable to extend with.
        """
        for item in items:
            self.append(item)

    def leftextend(self, items: Iterable[Point]) -> None:
        """
        Extend our items to the left with an iterable's items.

        Args:
            items: The iterable to extend with.
        """
        for item in items:
            self.appendleft(item)

    def NEMids(self) -> List[NEMid]:
        """
        Obtain all NEMids in the strand, only.

        Utilizes self.items.NEMids() to obtain the NEMids.

        Returns:
            A list of NEMids in the strand.
        """
        return self.items.NEMids()

    def nucleosides(self) -> List["Nucleoside"]:
        """
        Obtain all nucleosides in the strand, only.

        Utilizes self.items.nucleosides() to obtain the nucleosides.

        Returns:
            A list of nucleosides in the strand.
        """
        return self.items.nucleosides()

    @property
    def sequence(self):
        return [nucleoside.base for nucleoside in self.nucleosides()]

    @sequence.setter
    def sequence(self, new_sequence: List[str]):
        nucleosides = self.nucleosides()
        if len(new_sequence) == len(nucleosides):
            for index, base in enumerate(new_sequence):
                our_nucleoside = nucleosides[index]
                our_nucleoside.base = base

                matching_nucleoside = our_nucleoside.matching()
                if matching_nucleoside is not None:
                    matching_nucleoside.base = our_nucleoside.complement
        else:
            raise ValueError(
                f"Length of the new sequence ({len(new_sequence)}) must"
                + "match number of nucleosides in strand ({len(self)})"
            )

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
        for nucleoside in self.nucleosides():
            if overwrite or nucleoside.base is None:
                nucleoside.base = random.choice(DNA)
                nucleoside.styles.reset()
                if (matching := nucleoside.matching()) is not None:
                    matching.base = nucleoside.complement

    def clear_sequence(self, overwrite: bool = False) -> None:
        """
        Clear the sequence of the strand.

        Args:
            overwrite: Whether to overwrite the current sequence or not. If
                overwrite is True then all set nucleosides that are set (are not
                None) will be made None.
        """
        for nucleoside in self.nucleosides():
            if overwrite or nucleoside.base is not None:
                nucleoside.base = None

    def index(self, item) -> int | None:
        """Determine the index of an item."""
        try:
            return self.items.index(item)
        except IndexError:
            return None

    def sliced(self, start: int | None, end: int | None) -> list:
        """Return self.NEMids as a list."""
        return StrandItems(itertools.islice(self.items, start, end))

    def touching(self, other: "Strand") -> bool:
        """
        Check whether this strand is touching a different strand.

        Args:
            other: The strand potentially touching this one.
        """
        for our_item in shuffled(self.NEMids()):
            for their_item in shuffled(other.NEMids()):
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
        checks = [bool(NEMid_.direction) for NEMid_ in self.NEMids()]
        return all(checks)

    def down_strand(self) -> bool:
        """Whether the strand is a down strand."""
        checks = [(not bool(NEMid_.direction)) for NEMid_ in self.NEMids()]
        return all(checks)

    def cross_screen(self) -> bool:
        """
        Whether the strand wraps across the screen.

        This is determined by checking to see if any active junctions are cross screen.

        Returns:
            True if the strand wraps across the screen, False otherwise.
        """
        junctions = filter(lambda NEMid_: NEMid_.junction, self.NEMids())
        for junction in junctions:
            if abs(junction.x_coord - junction.juncmate.x_coord) > 1:
                return True
        return False

    def interdomain(self) -> bool:
        """Whether all the items in this strand belong to the same domain."""
        domains = [item.domain for item in self.items]

        if len(domains) == 0:
            return False
        checker = domains[0]
        for domain in domains:
            if domain is not checker:
                return True

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
