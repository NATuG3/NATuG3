from typing import List

from datatypes.points import NEMid


class Strand(list):
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
