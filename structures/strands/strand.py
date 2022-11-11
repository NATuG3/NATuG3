from dataclasses import dataclass
from functools import cached_property
from math import dist
from random import shuffle
from typing import List, Tuple, Type

import settings
from structures.points import NEMid


def shuffled(array):
    output = list(array)
    shuffle(output)
    return output


@dataclass
class Strand:
    """
    A strand of items.

    Attributes:
        items: All items contained within the strand (NEMids, Nicks, etc.).
        NEMids: All NEMids contained within the strand.
        color (tuple[int, int, int]): RGB color of strand.
        closed (bool): Whether the strand is closed.
        empty (bool): Whether the strand is empty.
        boundaries (tuple[minX, maxX, minY, maxY]): The boundary box of the strand.
        up_strand (bool): Whether all NEMids in this strand are up-NEMids.
        down_strand (bool): Whether all NEMids in this strand are down-NEMids.
        interdomain (bool): Whether this strand spans multiple domains.
    """

    items: list
    color: Tuple[int, int, int] = (0, 0, 0)

    def __post_init__(self):
        """
        Initialize a Strand object.

        Args:
            items: All items in the strand.
            color: The color of the strand as (R, G, B). Defaults to black.
        """
        # make our items immutable
        self.items, tuple(self.items)

        # assign all our NEMids US as the parent strand
        for index, NEMid_ in enumerate(self.items):
            self.items[index].strand = self

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

    def split(self, NEMid_: NEMid) -> Tuple[Type["Strand"], Type["Strand"]]:
        """
        Split strand at NEMid NEMid_.

        Args:
            NEMid_: The NEMid to remove, resulting in a split strand.
        """
        return [self.__init__(NEMid_.strand[:NEMid_.index]), self.__init__(NEMid_.strand[NEMid_.index:])]

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

    @cached_property
    def empty(self) -> bool:
        """Whether this strand is empty."""
        return len(self.items) <= 0

    @cached_property
    def closed(self) -> bool:
        """Whether this strand is closed."""
        try:
            return (
                dist(self.items[0].position(), self.items[-1].position())
                < settings.junction_threshold
            )
        except AttributeError:
            return False

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
        """The overall size of the strand in nanometers."""
        width = max([item.x_coord for item in self.items]) - min(
            [item.x_coord for item in self.items]
        )
        height = max([item.z_coord for item in self.items]) - min(
            [item.z_coord for item in self.items]
        )
        return width, height

    @cached_property
    def boundaries(self) -> Tuple[float, float, float, float]:
        """The location of the bounding box of the strand."""
        return (
            min(item.x_coord for item in self.items),
            max(item.x_coord for item in self.items),
            min(item.z_coord for item in self.items),
            max(item.z_coord for item in self.items),
        )
