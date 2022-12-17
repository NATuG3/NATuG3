import itertools
import random
from collections import deque
from contextlib import suppress
from dataclasses import dataclass, field
from functools import cached_property
from typing import Tuple, Iterable, Deque, List, ClassVar, Literal

from constants.bases import DNA
from constants.directions import RIGHT, LEFT, UP
from structures.domains import Domain
from structures.points import NEMid, Nucleoside
from structures.points.point import Point
from structures.profiles import NucleicAcidProfile


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
        name: The user-set name of the strand. This appears when exporting, and is used as a title.
        color: The RGB color of the strand. This is a tuple of 3 integers, each between 0 and 255.
        auto_color: A flag to determine whether a Strands parent should automatically color this strand when its
            restyle() method is called.
        thickness: The thickness of the strand. This is an integer representing the number of pixels wide the strand.
        auto_thickness: A flag to determine whether a Strands parent should automatically set the thickness of this
            strand when its restyle() method is called.
        items: The items in the strand. This is a deque of Points.
        nucleic_acid_profile: The nucleic acid settings used.
        sequence (list): The sequence of the strand.
            This is a list of all the bases of all the nucleosides in the strand.
        closed: Whether the strand is closed. Must be manually set.
        empty: Whether the strand is empty. This is equivalent to len(self) == 0.
        up_strand: Whether all NEMids in this strand are up-NEMids.
            Recursively checks all items in the strand.
        down_strand: Whether all NEMids in this strand are down-NEMids.
            Recursively checks all items in the strand
        interdomain: Whether this strand spans multiple domains.
            Recursively checks all items in the strand to see if any items have unique domains
            from the other items.
        cross_screen: Whether this strand wraps across the screen.

    Methods:
        append(item): Add an item to the right of the strand.
        appendleft(item): Add an item to the left of the strand.
        extend(items): Extend our items to the right with an iterable's items.
        extendleft(items): Extend our items to the left with an iterable's items.
        NEMids(): Obtain all NEMids in the strand, only.
        nucleosides(): Obtain all nucleosides in the strand, only.
        index(item): Determine the index of an item.
        sliced(from, to): Return self.NEMids as a list.
        clear_sequence(overwrite): Clear the sequence of the strand.
        randomize_sequence(overwrite): Randomize the sequence of the strand.
    """

    name: str = "Strand"
    parent: "Strands" = None

    nucleic_acid_profile: NucleicAcidProfile = field(default_factory=NucleicAcidProfile)
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

    __cached: ClassVar[Tuple[str]] = (
        "up_strand",
        "down_strand",
        "interdomain",
        "cross_screen",
        "nucleosides",
    )

    def vertical_shift(self, distance: float) -> None:
        """
        Shift the Z coord of all items in the strand by a certain amount.

        Args:
            distance: The amount to shift by. This is in nanometres.
        """
        for item in self.items:
            item.z_coord += distance

    def horizontal_shift(self, distance: float) -> None:
        """
        Shift the X coord of all items in the strand by a certain amount.

        Args:
            distance: The amount to shift by. This is in nanometres.
        """
        for item in self.items:
            item.x_coord += distance

    def generate_NEMids(
        self, count: int, domain: Domain | None, direction: Literal[0, 1] = RIGHT
    ) -> None:
        """
        Generate additional NEMids and Nucleosides for the strand.

        This creates new NEMid and Nucleoside objects which are inserted into and parented to this strand.

        Args:
            count: The number of additional NEMids to generate. Nucleosides are generated automatically, this is
                specifically an integer number of NEMids.
            domain: The domain to use for x coord generation in the NEMid generation process. If this is None the
                domain of the right most NEMid is used by default.
            direction: The direction to generate the NEMids in. This is either RIGHT or LEFT. If LEFT NEMids are
                generated and left-appended to the left of the strand; if RIGHT NEMids are generated and appended to the
                right side of the strand.

        Notes:
            Items are appended directly to the left or right side of the strand, and are not returned. The strand
            object is updated in place.
        """
        # Compute variables dependent on direction.
        # Edge_NEMid == rightmost or leftmost NEMid based off of the direction that we're generating NEMids in.
        # Modifier == whether we are increasing or decreasing angles/z-coords as we progress. Takes the form of -1 or 1
        # so that we can multiply it by the changes.
        if direction == RIGHT:
            edge_NEMid = self.NEMids()[-1]
            modifier = 1
        elif direction == LEFT:
            edge_NEMid = self.NEMids()[0]
            modifier = -1
        else:
            raise ValueError(f"Invalid direction: %s", direction)

        # If they do not pass a Domain object, use the domain of the right most NEMid
        domain = domain if domain is not None else edge_NEMid.domain

        # Create a generator for angles. The angle generator begins at the angle of the item rightmost in the list,
        # and yields angles increasing by theta_b. We slice the angle generator so that it stops yielding after count
        # number of NEMids have been generated. As it yields, we apply a modulo operation to the angle to ensure that
        # angles do not exceed 360 degrees.
        angle_generator = itertools.count(
            edge_NEMid.angle, self.nucleic_acid_profile.theta_b*modifier
        )
        angle_generator = itertools.islice(angle_generator, count)
        angle_generator = map(lambda angle_: angle_ % 360, angle_generator)

        # Create a generator for x coordinates. The x coordinates are generated based off of the angles, so this uses
        # the above angle generator and mapping the Point.x_coord_from_angle() method onto it to transform the angles
        # into x coordinates.
        x_coord_generator = map(
            lambda angle_: Point.x_coord_from_angle(angle_, domain), angle_generator
        )
        x_coord_generator = itertools.islice(x_coord_generator, count)

        # Create a generator for z coordinates. The z coordinate generator begins at the last z coordinate in the
        # strand and yields z coordinates increasing by Z_b. We slice the z coordinate generator so that it stops
        # yielding after count number of NEMids have been generated.
        z_coord_generator = itertools.count(
            edge_NEMid.z_coord, self.nucleic_acid_profile.Z_b*modifier
        )
        z_coord_generator = itertools.islice(z_coord_generator, count)

        # Iterate over the various generators and create NEMids and Nucleosides. Then append them to the strand.
        for angle, x_coord, z_coord in zip(
            angle_generator, x_coord_generator, z_coord_generator
        ):
            # Create a NEMid object with the data from the generators.
            NEMid_ = NEMid(
                angle=angle,
                x_coord=x_coord,
                z_coord=z_coord,
            )

            # Create a Nucleoside object from the NEMid object's data.
            nucleoside = NEMid.to_nucleoside()

            # If we are generating upwards boost the nucleoside up/down to be the next item in the strand.
            nucleoside.angle += self.nucleic_acid_profile.theta_b / 2 * modifier
            nucleoside.z_coord += self.nucleic_acid_profile.Z_b / 2 * modifier
            nucleoside.x_coord = Point.x_coord_from_angle(nucleoside.angle, nucleoside.domain)

            # append the new NEMid and nucleoside to the right/left side of the strand based off of the direction.
            if direction == RIGHT:
                # right append
                self.append(NEMid_)
                self.append(nucleoside)
            else:
                # left append
                self.appendleft(NEMid_)
                self.appendleft(nucleoside)

    def append(self, item: Point) -> None:
        """Add an item to the right of the strand."""
        self.items.append(item)
        self.NEMids.cache_clear()
        self.nucleosides.cache_clear()

    def appendleft(self, item: Point):
        """
        Add an item to the left of the strand.

        Args:
            item: The item to add.
        """
        self.items.appendleft(item)

    def extend(self, item: Iterable[Point]) -> None:
        """
        Extend our items to the right with an iterable's items.

        Args:
            item: The iterable to extend with.
        """
        self.items.extend(item)

    def extendleft(self, item: Iterable[Point]) -> None:
        """
        Extend our items to the left with an iterable's items.

        Args:
            item: The iterable to extend with.
        """
        self.items.extendleft(item)

    def NEMids(self) -> List[NEMid]:
        """
        Obtain all NEMids in the strand, only.

        Works by recursively checking the type of items in self.items.

        Returns:
            List of all nucleosides in strand.items.
        """
        return list(filter(lambda item: isinstance(item, NEMid), self.items))

    def nucleosides(self):
        """
        Obtain all nucleosides in the strand, only.

        Works by recursively checking the type of items in self.items.

        Returns:
            List of all nucleosides in strand.items.
        """
        return list(filter(lambda item: isinstance(item, Nucleoside), self.items))

    def __len__(self) -> int:
        """Obtain number of items in strand."""
        return len(self.items)

    def __contains__(self, item) -> bool:
        """Determine whether item is in strand."""
        return item in self.items

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
            overwrite: Whether to overwrite the current sequence or not. If overwrite is False then all unset
                nucleosides (ones which are None) will be set to a random nucleoside. If overwrite is True then all
                nucleosides will be set to a random nucleoside.
        """
        for nucleoside in self.nucleosides():
            if overwrite or nucleoside.base is None:
                nucleoside.base = random.choice(DNA)
                nucleoside.matching().base = nucleoside.complement

    def clear_sequence(self, overwrite: bool = False) -> None:
        """
        Clear the sequence of the strand.

        Args:
            overwrite: Whether to overwrite the current sequence or not. If overwrite is True then all set nucleosides
                that are set (are not None) will be made None.
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

    def recompute(self) -> None:
        """Clear cached methods, and reassign juncmates, and recompute nucleosides."""
        # clear all cache
        for cached in self.__cached:
            with suppress(KeyError):
                del self.__dict__[cached]

        # assign all our items to have us as their parent strand
        for index, item in enumerate(self.items):
            self.items[index].strand = self

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

    @cached_property
    def up_strand(self) -> bool:
        """Whether the strand is an up strand."""
        checks = [bool(NEMid_.direction) for NEMid_ in self.NEMids()]
        return all(checks)

    @cached_property
    def down_strand(self) -> bool:
        """Whether the strand is a down strand."""
        checks = [(not bool(NEMid_.direction)) for NEMid_ in self.NEMids()]
        return all(checks)

    @cached_property
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

    @cached_property
    def interdomain(self) -> bool:
        """Whether all the NEMids in this strand belong to the same domain."""
        domains = [NEMid_.domain for NEMid_ in self.NEMids()]

        if len(domains) == 0:
            return False
        checker = domains[0]
        for domain in domains:
            if domain is not checker:
                return True
        return False

    @cached_property
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
