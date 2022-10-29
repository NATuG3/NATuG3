from math import dist
from typing import List

import settings
from datatypes.points import Point, NEMid


class Strand(list):
    """
    A strand of NEMids.

    Attributes:
        color (tuple[int, int, int]): RGB color of strand.
    """

    def __init__(self, points: List[Point], color=(0, 0, 0)):
        super().__init__(points)
        self.color = color

    def create_junction(self, other_NEMid: NEMid):
        """
        Create a junction between this and another strand.

        Args:
            other_NEMid (NEMid): A NEMid of another strand to create a junction at.

        Returns:
            tuple: (top-strand, bottom-strand)
        """
        for NEMid_ in self:
            if dist(NEMid_.position, other_NEMid) < settings.junction_threshold:
                continue
            else:
                break
        else:  # for statement was broken
            raise ValueError("other_NEMid has no overlaps with this strand's NEMids.")
