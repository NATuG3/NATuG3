from collections import deque
from math import dist
from random import shuffle
from typing import List, Tuple

from structures.points import NEMid


class Strand:
    """
    A strand of NEMids.

    Attributes:
        color (tuple[int, int, int]): RGB color of strand.
    """

    def __init__(self, NEMids: List[NEMid], color=(0, 1, 2)):
        self.NEMids = NEMids
        self.color = color
        self.assign_strands()

    def assign_strands(self):
        # assign strand to NEMids
        for index, NEMid_ in enumerate(self.NEMids):
            self.NEMids[index].strand = self

    def touching(self, other, touching_distance=.1) -> bool:
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

        for our_NEMid in shuffled(self.NEMids):
            for their_NEMid in shuffled(other.NEMids):
                if dist(our_NEMid.position(), their_NEMid.position()) < touching_distance:
                    return True
        return False

    @property
    def up_strand(self):
        return all([bool(NEMid_.direction) for NEMid_ in self.NEMids])

    @property
    def down_strand(self):
        return all([(not bool(NEMid_.direction)) for NEMid_ in self.NEMids])

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
        width = max([NEMid_.x_coord for NEMid_ in self.NEMids]) - min(
            [NEMid_.x_coord for NEMid_ in self.NEMids]
        )
        height = max([NEMid_.z_coord for NEMid_ in self.NEMids]) - min(
            [NEMid_.z_coord for NEMid_ in self.NEMids]
        )
        return width, height

    @property
    def location(self) -> Tuple[float, float, float, float]:
        """The location of the bounding box of the strand in nanometers."""
        return (
            min(NEMid_.x_coord for NEMid_ in self.NEMids),
            max(NEMid_.x_coord for NEMid_ in self.NEMids),
            min(NEMid_.z_coord for NEMid_ in self.NEMids),
            max(NEMid_.z_coord for NEMid_ in self.NEMids)
        )

    @property
    def is_closed(self) -> bool:
        """Return whether this is a closed strand or not."""
        return self.NEMids[0] == self.NEMids[-1]
