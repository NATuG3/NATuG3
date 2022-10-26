from datatypes.points import NEMid


class Strand(list):
    """
    A strand of NEMids.

    Attributes:
        color (tuple[int, int, int]): RGB color of strand.
    """

    def __init__(self, *args: NEMid, color=(0, 0, 0)):
        super().__init__(*args)
        self.color = color
