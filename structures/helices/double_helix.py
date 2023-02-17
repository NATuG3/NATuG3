from constants.directions import DOWN, UP
from utils import inverse
from structures.helices.helix import Helix


class DoubleHelix:
    """
    A container storing the two helices of a double helix.

    This class lets you reference a given helix by its zeroedness (zeroed or other),
    direction (up or down), or domain helical joint (left or right).

    Attributes:
        zeroed_helix: The helix that is lined up with the previous double helix on
            the left side. The opposite helix is the "other helix".
        other_helix: The other helix in the same domain as the zeroed helix. This is,
            by definition, the helix that is not the zeroed helix.
        up_helix: The helix that has progresses upwards from its 5' to 3' end of the
            strand. This is also known as the up helix.
        down_helix: The helix that has progresses downwards from its 5' to 3' end of
            the strand. This is also known as the down helix.
        left_helix: The helix that is of the direction of the domain's left helical
            joint. This is the helix whose points are lined up to the points that are
            on the helix of the previous domain's right helical joint helix.
        right_helix: The helix that is of the direction of the domain's right helical
            joint. This is the helix whose points are lined up to the points that are
            on the helix of the next domain's left helical joint helix.
    """

    __slots__ = "domain", "helices"

    def __init__(
        self,
            domain: "Domain",
            up_helix: Helix,
            down_helix: Helix,
    ) -> None:
        """
        Initialize a double helix.

        Args:
            domain: The domain that the double helix is to be in.
            up_helix: The helix that progresses upwards from its 5' to 3' end.
            down_helix: The helix that progresses downwards from its 5' to 3' end.
        """
        self.domain = domain
        self.helices = (up_helix, down_helix)
        self.up_helix.direction = UP
        self.down_helix.direction = DOWN

    def __getitem__(self, item):
        if item in (DOWN, UP):
            return self[item]

    def __iter__(self):
        return iter(self.helices)

    @property
    def left_helix(self) -> Helix:
        """
        The helix that is on the left side of the domain and is thus lined up with
        the previous domain's right helical joint.
        """
        return self[self.domain.left_helix_joint]

    @property
    def right_helix(self) -> Helix:
        """
        The helix that is on the right side of the domain and is thus lined up with the
        next domain's left helical joint.
        """
        return self[self.domain.right_helix_joint]

    @property
    def up_helix(self) -> Helix:
        """
        The helix that has progresses upwards from its 5' to 3' ends.
        """
        return self[UP]

    @property
    def down_helix(self) -> Helix:
        """
        The helix that has progresses downwards from its 5' to 3' ends.
        """
        return self[DOWN]

    @property
    def zeroed_helix(self) -> Helix:
        """
        The helix that is lined up with the previous double helix on the left side.
        """
        return self[self.domain.left_helix_joint]

    @property
    def other_helix(self) -> Helix:
        """
        The other helix in the same domain as the zeroed helix.
        """
        return self[inverse(self.domain.left_helix_joint)]
