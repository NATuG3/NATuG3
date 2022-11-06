from collections import deque
from math import dist
from random import shuffle
from typing import List, Tuple, Type

from structures.points import NEMid


class Strand:
    """
    A strand of NEMids.

    Attributes:
        items: An iterable of all NEMids.
        color (tuple[int, int, int]): RGB color of strand.
    """

    def __init__(self, NEMids: List[NEMid], color=(0, 1, 2)):
        self.items = deque(NEMids)
        self.color = color
        self.assign_strands()

    def assign_strands(self):
        """Set NEMid.Strand to be self for all items in self."""
        for index, NEMid_ in enumerate(self.items):
            self.items[index].strand = self

    def touching(self, other: Type["Strand"], touching_distance=0.22) -> bool:
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
    def up_strand(self):
        checks = []
        for item in self.items:
            if isinstance(item, NEMid):
                checks.append(bool(item.direction))
        return all(checks)

    @property
    def down_strand(self):
        checks = []
        for item in self.items:
            if isinstance(item, NEMid):
                checks.append(not bool(item.direction))
        return all(checks)

    @property
    def interdomain(self) -> bool:
        """Whether all the NEMids in this strand belong to the same domain."""
        domains = []
        for item in self.items:
            if isinstance(item, NEMid):
                domains.append(item)
        domains = [NEMid_.domain for NEMid_ in domains]

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
        width = max([NEMid_.x_coord for NEMid_ in self.items]) - min(
            [NEMid_.x_coord for NEMid_ in self.items]
        )
        height = max([NEMid_.z_coord for NEMid_ in self.items]) - min(
            [NEMid_.z_coord for NEMid_ in self.items]
        )
        return width, height

    @property
    def location(self) -> Tuple[float, float, float, float]:
        """The location of the bounding box of the strand in nanometers."""
        return (
            min(NEMid_.x_coord for NEMid_ in self.items),
            max(NEMid_.x_coord for NEMid_ in self.items),
            min(NEMid_.z_coord for NEMid_ in self.items),
            max(NEMid_.z_coord for NEMid_ in self.items),
        )

    @property
    def is_closed(self) -> bool:
        """Return whether this is a closed strand or not."""
        return self.items[0] == self.items[-1]
