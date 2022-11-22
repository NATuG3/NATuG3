import itertools
from collections import deque
from contextlib import suppress
from functools import cached_property
from math import dist
from random import shuffle
from typing import List, Tuple, Type

import settings
from structures.points import NEMid


def shuffled(iterable):
    """Shuffle an iterable and return a copy."""
    output = list(iterable)
    shuffle(output)
    return output


class Strand:
    """
    A strand of items.

    Attributes:
        items: All items contained within the strand (NEMids, Nicks, etc.).
        NEMids: All NEMids contained within the strand.
        color (tuple[int, int, int]): RGB color of strand.
        closed (bool): Whether the strand is closed. Must be manually set.
        empty (bool): Whether the strand is empty.
        boundaries (tuple[minX, maxX, minY, maxY]): The boundary box of the strand.
        up_strand (bool): Whether all NEMids in this strand are up-NEMids.
        down_strand (bool): Whether all NEMids in this strand are down-NEMids.
        interdomain (bool): Whether this strand spans multiple domains.
    """

    __cached = ("NEMids", "up_strand", "down_strand", "interdomain", "boundaries")

    def __init__(
        self,
        items: list = None,
        color: Tuple[int, int, int] = (0, 0, 0),
        closed: bool | None = False,
        parent: Type["Strands"] = None,
    ):
        """
        Initialize the strand object.

        Args:
            items: All items to place inside the strand. Order sensitive.
            color: RGB color for the strand. Defaults to black.
            closed: Whether the strand is closed. Defaults to False.
            parent: The parent Strands object. Defaults to None.
        """
        self.color = color
        self.closed = closed
        self.parent = parent

        if items is None:
            self.items = deque([])
        elif isinstance(items, deque):
            self.items = items
        else:
            self.items = deque(items)

    def __len__(self) -> int:
        """Obtain number of items in strand."""
        return len(self.items)

    def __contains__(self, item) -> bool:
        """Determine whether item is in strand."""
        return item in self.items

    @property
    def index(self):
        """Obtain the index of this strand with respect to the parent strand. None if parent strand is None."""
        if self.parent is None:
            return None
        return self.parent.strands.index(self)

    def sliced(self, start: int, end: int) -> list:
        """Return self.items as a list."""
        return list(itertools.islice(self.items, start, end))

    def recompute(self) -> None:
        """Clear cached methods."""
        # clear all cache
        for cached in self.__cached:
            with suppress(KeyError):
                del self.__dict__[cached]

        # assign all our items to have us as their parent strand
        for index, item in enumerate(self.items):
            self.items[index].strand = self

            # assign juncmates
            if isinstance(item, NEMid) and item.junctable:
                for test_item in self.items:
                    if test_item is item:
                        continue
                    elif (
                        dist(item.position(), test_item.position())
                        < settings.junction_threshold
                    ):
                        item.juncmate = test_item
                        test_item.juncmate = item

    def touching(self, other: Type["Strand"], touching_distance=0.2) -> bool:
        """
        Check whether this strand is touching a different strand.

        Args:
            other: The strand potentially touching this one.
            touching_distance: The distance to be considered touching.
        """
        # check boundary boxes of the strands before doing heavy touch-check computations
        if (self.boundaries[0] + self.size[0] > other.boundaries[0]) or (
            self.boundaries[1] + self.size[1] > other.boundaries[1]
        ):  # if our bottom left corner x coord + our width is greater than their bottom left corner than we overlap
            for our_item in shuffled(self.items):
                for their_item in shuffled(other.items):
                    # for each item in us, for each item in them, check if we are sufficiently close
                    if (
                        dist(our_item.position(), their_item.position())
                        < touching_distance
                    ):
                        # if we've detected that even a single item touches, we ARE touching
                        return True
        else:
            # we were not touching
            return False

    @cached_property
    def NEMids(self) -> List[NEMid]:
        """
        Obtain all NEMids in the strand.

        Returns:
            list: All NEMids in the strand.
        """
        output = []
        for item in self.items:
            if isinstance(item, NEMid):
                output.append(item)
        return output

    @property
    def empty(self) -> bool:
        """Whether this strand is empty."""
        return len(self.items) == 0

    @cached_property
    def up_strand(self) -> bool:
        """Whether the strand is an up strand."""
        checks = [bool(NEMid_.direction) for NEMid_ in self.NEMids]
        return all(checks)

    @cached_property
    def down_strand(self) -> bool:
        """Whether the strand is a down strand."""
        checks = [(not bool(NEMid_.direction)) for NEMid_ in self.NEMids]
        return all(checks)

    @cached_property
    def interdomain(self) -> bool:
        """Whether all the NEMids in this strand belong to the same domain."""
        domains = [NEMid_.domain for NEMid_ in self.NEMids]

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

    @cached_property
    def boundaries(self) -> Tuple[float, float, float, float]:
        """
        The location of the bounding box of the strand.

        Returns:
            Tuple[xMin, xMax, zMin, zMax]: The boundary box of the strand.
        """
        return (
            min(item.x_coord for item in self.items),
            max(item.x_coord for item in self.items),
            min(item.z_coord for item in self.items),
            max(item.z_coord for item in self.items),
        )
