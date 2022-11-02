from collections import deque
from math import inf
from typing import List

from datatypes.points import NEMid


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

    def append(self, NEMid_) -> None:
        NEMid_.strand = self
        super().append(NEMid_)

    @property
    def is_closed(self):
        """Return whether this is a closed strand or not."""
        return self[0] == self[-1]

    @property
    def loops_down(self):
        """Whether the top of the strand loops upwards."""
        previous_z_coord = inf
        for NEMid_ in self:
            NEMid_: NEMid
            if NEMid_.z_coord < previous_z_coord:
                return True
        return False

    @property
    def loops_up(self):
        """Whether the bottom of the strand loops upwards."""
        previous_z_coord = -inf
        for NEMid_ in self:
            NEMid_: NEMid
            if NEMid_.z_coord > previous_z_coord:
                return True
        return False
