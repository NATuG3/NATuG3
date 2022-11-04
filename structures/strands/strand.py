from collections import deque
from typing import List

from structures.points import NEMid


class Strand(deque):
    """
    A strand of NEMids.

    Attributes:
        color (tuple[int, int, int]): RGB color of strand.
    """

    def __init__(self, NEMids: List[NEMid], color=(0, 0, 0)):
        super().__init__(NEMids)

        # assign strand to NEMids
        for index, NEMid_ in enumerate(NEMids):
            self[index].strand = self

        self.color = color

    @property
    def size(self):
        """The overall size of the strand in nanometers."""
        width = max([NEMid_.x_coord for NEMid_ in self]) - min(
            [NEMid_.x_coord for NEMid_ in self]
        )
        height = max([NEMid_.z_coord for NEMid_ in self]) - min(
            [NEMid_.z_coord for NEMid_ in self]
        )
        return width, height

    @property
    def location(self):
        """The location of the bounding box of the strand in nanometers."""
        return (
            min(NEMid_.x_coord for NEMid_ in self),
            max(NEMid_.x_coord for NEMid_ in self),
            min(NEMid_.z_coord for NEMid_ in self),
            max(NEMid_.z_coord for NEMid_ in self)
        )

    @property
    def greyscale(self):
        if self.color[0] == self.color[1] == self.color[2]:
            return True
        else:
            return False

    def append(self, NEMid_) -> None:
        NEMid_.strand = self
        super().append(NEMid_)

    @property
    def is_closed(self):
        """Return whether this is a closed strand or not."""
        return self[0] == self[-1]
