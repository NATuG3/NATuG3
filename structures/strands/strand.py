from collections import deque
from math import dist
from random import shuffle
from typing import List, Tuple, Type

import settings
from structures.points import NEMid


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

    def __init__(self, items: list, color: Tuple[int, int, int] = (0, 1, 2)):
        """
        Initialize a Strand object.

        Args:
            items: All items in the strand.
            color: The color of the strand as (R, G, B). Defaults to (1, 2, 3).
        """
        self.items: deque = deque(items)
        self.color: Tuple[int, int, int] = color
        self.assign_strands()

    def assign_strands(self):
        """Set NEMid.Strand to be self for all items in self."""
        for index, NEMid_ in enumerate(self.items):
            self.items[index].strand = self

    def touching(self, other: Type["Strand"], touching_distance=0.25) -> bool:
        """
        Check whether this strand is touching a different strand.

        Args:
            other: The strand potentially touching this one.
            touching_distance: The distance to be considered touching.
        """

        def shuffled(array):
            output = list(array)
            shuffle(output)
            return output

        for our_item in shuffled(self.items):
            for their_item in shuffled(other.items):
                if (
                        dist(our_item.position(), their_item.position())
                        < touching_distance
                ):
                    return True
        return False

    @property
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
        return len(self.items) <= 0

    @property
    def closed(self) -> bool:
        """Whether this strand is closed."""
        try:
            return dist(self.items[0].position(), self.items[-1].position()) < settings.junction_threshold
        except AttributeError:
            return False

    @property
    def up_strand(self) -> bool:
        """Whether the strand is an up strand."""
        checks = [bool(NEMid_.direction) for NEMid_ in self.NEMids]
        return all(checks)

    @property
    def down_strand(self) -> bool:
        """Whether the strand is a down strand."""
        checks = [(not bool(NEMid_.direction)) for NEMid_ in self.NEMids]
        return all(checks)

    @property
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

    @property
    def size(self) -> Tuple[float, float]:
        """The overall size of the strand in nanometers."""
        width = max([item.x_coord for item in self.items]) - min(
            [item.x_coord for item in self.items]
        )
        height = max([item.z_coord for item in self.items]) - min(
            [item.z_coord for item in self.items]
        )
        return width, height

    @property
    def boundaries(self) -> Tuple[float, float, float, float]:
        """The location of the bounding box of the strand."""
        return (
            min(item.x_coord for item in self.items),
            max(item.x_coord for item in self.items),
            min(item.z_coord for item in self.items),
            max(item.z_coord for item in self.items),
        )