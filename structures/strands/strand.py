import itertools
import random
from collections import deque
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Tuple, Iterable, Deque, List, Type

import numpy as np

from constants.bases import DNA
from constants.directions import *
from structures.points import NEMid, Nucleoside
from structures.points.point import Point
from structures.profiles import NucleicAcidProfile
from structures.utils import converge_point_data


def shuffled(iterable: Iterable) -> list:
    """Shuffle an iterable and return a copy."""
    output = list(iterable)
    random.shuffle(output)
    return output


@dataclass
class Strand:
    """
    A strand of items.

    Attributes:
        name: The user-set name of the strand. This appears when exporting, and is used
            as a title.
        color: The RGB color of the strand. This is a tuple of 3 integers, each between
            0 and 255.
        auto_color: A flag to determine whether a Strands parent should automatically
            color this strand when its restyle() method is called.
        thickness: The thickness of the strand. This is an integer representing the
            number of pixels wide the strand.
        auto_thickness: A flag to determine whether a Strands parent should
            automatically set the thickness of this strand when its restyle() method
            is called.
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
    """

    name: str = "Strand"
    parent: "Strands" = None

    nucleic_acid_profile: NucleicAcidProfile = field(
        default_factory=NucleicAcidProfile, repr=False
    )
    items: Deque[Point] = field(default_factory=deque)
    closed: bool = False

    color: Tuple[int, int, int] = (
        0,
        0,
        0,
    )
    auto_color: bool = True
    thickness: int = 2
    auto_thickness: bool = True
    highlighted: bool = False

    def __post_init__(self):
        self.items = deque(self.items)
        for item in self.items:
            item.strand = self

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

        # Set the items of the new strands
        strand1.items = self.sliced(0, index)
        strand2.items = self.sliced(index + 1, None)

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
        """Remove <count> number of items from the right side of the strand."""
        for i in range(count):
            self.items.pop().strand = None

    def lefttrim(self, count: int):
        """Remove <count> number of items from the left side of the strand."""
        for i in range(count):
            self.items.popleft().strand = None

    def generate(
        self,
        count: int,
        domain: "Domain" = None,
        initial_angle: int = None,
        initial_z_coord: int = None,
        initial_type: Type[Nucleoside] | Type[NEMid] = None,
        direction: int = None,
    ) -> None:
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
            initial_angle: The angle to use for the first NEMid generated. If this is
                None, the angle of the right/left most NEMid is used by default. This
                is required if the strand is empty.
            initial_z_coord: The z coord to use for the first NEMid generated. If this
                is None, the z coord of the right/left most NEMid is used by default.
                This is required if the strand is empty.
            initial_type: The type to use for the first item generated. Either
                Nucleoside or NEMid. If this is None, the type of the right/left most
                NEMid is used by default. This is required if the strand is empty.
            direction: The direction to apply to the items generated. If this is None,
                the direction of the right/left most NEMid is used by default. This is
                required if the strand is empty.
        """

        # Compute variables dependent on direction. Edge_NEMid == rightmost or
        # leftmost NEMid based off of the direction that we're generating NEMids in.
        # Modifier == whether we are increasing or decreasing angles/z-coords as we
        # progress. Takes the form of -1 or 1 so that we can multiply it by the
        # changes.
        if count > 0 or len(self) == 1:
            # If we're generating to the right, the edge NEMid is the rightmost NEMid.
            edge_item = self[-1] if len(self) > 0 else None
            modifier = 1
        elif count < 0:
            # If we're generating to the left, the edge item is the leftmost item.
            edge_item = self[0] if len(self) > 0 else None
            modifier = -1
        else:
            # If count == 0, then we don't need to do anything.
            return

        # Create easy referneces for various nucleic acid setting attributes. This is to
        # make the code more readable.
        theta_b = self.nucleic_acid_profile.theta_b
        Z_b = self.nucleic_acid_profile.Z_b

        # Obtain preliminary data
        domain = domain if domain is not None else edge_item.domain
        direction = direction if direction is not None else edge_item.direction
        initial_angle = (
            initial_angle
            if initial_angle is not None
            else edge_item.angle + ((theta_b / 2) * modifier)
        )
        initial_z_coord = (
            initial_z_coord
            if initial_z_coord is not None
            else edge_item.z_coord + ((Z_b / 2) * modifier)
        )
        if initial_type is None:
            if isinstance(edge_item, NEMid):
                initial_type = Nucleoside
            else:
                initial_type = NEMid

        # Compute the final angle and z coord based off of the initial values and the
        # number of NEMids to generate.
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
            initial_type=initial_type,
        )

        # Assign domains for all items
        for item in new_items:
            item.domain = domain
            item.direction = direction

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

        Works by recursively checking the type of items in self.items.

        Returns:
            List of all nucleosides in strand.items.
        """
        return [item for item in self.items if isinstance(item, NEMid)]

    def nucleosides(self) -> List["Nucleoside"]:
        """
        Obtain all nucleosides in the strand, only.

        Works by recursively checking the type of items in self.items.

        Returns:
            List of all nucleosides in strand.items.
        """
        return [item for item in self.items if isinstance(item, Nucleoside)]

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
                with suppress(AttributeError):
                    nucleoside.matching().base = nucleoside.complement

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
        return list(itertools.islice(self.items, start, end))

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
