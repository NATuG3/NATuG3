import itertools
from collections import deque
from contextlib import suppress
from dataclasses import dataclass, field
from functools import cached_property
from random import shuffle
from typing import Tuple, Type, Iterable, Deque, List, ClassVar


from structures.points import NEMid, Nucleoside
from structures.points.point import Point
from structures.profiles import NucleicAcidProfile


def shuffled(iterable: Iterable) -> list:
    """Shuffle an iterable and return a copy."""
    output = list(iterable)
    shuffle(output)
    return output


@dataclass
class Strand:
    """
    A strand of items.

    Attributes:
        nucleic_acid_profile: The nucleic acid settings used.
        sequence: The sequence of the strand.
        color: RGB color of strand.
        auto_color: Whether to automatically set the strand color.
        auto_thickness: Whether to automatically set the strand thickness.
        closed: Whether the strand is closed. Must be manually set.
        empty: Whether the strand is empty.
        up_strand: Whether all NEMids in this strand are up-NEMids.
        down_strand: Whether all NEMids in this strand are down-NEMids.
        interdomain: Whether this strand spans multiple domains.
        highlighted: Whether the strand is highlighted.
    """

    nucleic_acid_profile: field(default=NucleicAcidProfile, repr=False)
    items: Deque[Point] = field(default_factory=deque, repr=False)
    color: Tuple[int, int, int] = (0, 0, 0)
    auto_color: bool = True
    closed: bool = False
    highlighted: bool = False
    parent: Type["Strands"] = None

    __cached: ClassVar[Tuple[str]] = ("up_strand", "down_strand", "interdomain", "nucleosides")
    __supported_types: ClassVar[tuple[Type]] = (NEMid, Nucleoside)

    def __post_init__(self):
        self._thickness: ClassVar[int] = None
        self._NEMids: ClassVar[Tuple[NEMid] | None] = None
        self._nucleosides: ClassVar[Tuple[Nucleoside] | None] = None

    @property
    def thickness(self):
        """
        Automatically determine thickness if thickness is None.
        Otherwise, output the set thickness.
        """
        if self._thickness is None:
            if self.interdomain:
                return 9.5
            else:
                return 2
        else:
            return self._thickness

    @thickness.setter
    def thickness(self, new_thickness):
        """Change the currently set thickness."""
        self._thickness = new_thickness

    def append(self, item: Point):
        """Add an item to the right of the strand."""
        self.items.append(item)
        self.NEMids.cache_clear()
        self.nucleosides.cache_clear()

    def appendleft(self, item: Point):
        """Add an item to the left of the strand."""
        self.items.appendleft(item)
        self._NEMids = None
        self._nucleosides = None

    def extend(self, item: Iterable[Point]):
        """Extend our items to the right with an iterable's items."""
        self.items.extend(item)
        self._NEMids = None
        self._nucleosides = None

    def extendleft(self, item: Iterable[Point]):
        """Extend our items to the left with an iterable's items."""
        self.items.extendleft(item)
        self._NEMids = None
        self._nucleosides = None

    def NEMids(self):
        """
        Obtain all NEMids in the strand, only.

        Works by recursively checking the type of items in self.items.

        Args:
            listed: Returns the items listed if true. Otherwise, returns generator.

        Returns:
            List of all nucleosides in strand.items.
        """
        if self._NEMids is None:
            self._NEMids = tuple(filter(lambda item: isinstance(item, NEMid), self.items))
            return self._NEMids
        else:
            return self._NEMids

    def nucleosides(self):
        """
        Obtain all nucleosides in the strand, only.

        Works by recursively checking the type of items in self.items.

        Returns:
            List of all nucleosides in strand.items.
        """
        if self._nucleosides is None:
            self._nucleosides = tuple(filter(lambda item: isinstance(item, Nucleoside), self.items))
            return self._nucleosides
        else:
            return self._nucleosides

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
        if len(new_sequence) == len(self.nucleosides()):
            for index, base in enumerate(new_sequence):
                self.nucleosides()[index].base = base
                self.nucleosides()[index].matching.base = self.nucleosides()[index].complement
        else:
            raise ValueError(f"Length of the new sequence ({len(new_sequence)}) must" +
                             "match number of nucleosides in strand ({len(self)})")

    def index(self, item) -> int | None:
        """Determine the index of an item."""
        try:
            return self.items.index(item)
        except IndexError:
            return None

    def clear_pseudos(self) -> None:
        """Removes all pseudo items."""

        def pseudo_check(item):
            return not item.pseudo

        self.items = deque(filter(pseudo_check, self.items))

    def sliced(self, start: int, end: int) -> list:
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

    def touching(self, other: Type["Strand"], touching_distance=0.2) -> bool:
        """
        Check whether this strand is touching a different strand.

        Args:
            other: The strand potentially touching this one.
            touching_distance: The distance to be considered touching.
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
    def interdomain(self) -> bool:
        """Whether all the NEMids in this strand belong to the same domain."""
        domains = [NEMid_.domain for NEMid_ in self.NEMids()]

        if len(domains) == 0:
            return False
        checker = domains[0]
        for domain in domains:
            if domain != checker:
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
