from constants.directions import DOWN, UP
from structures.helices.helix import Helix
from utils import inverse


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
        up_helix: Helix | None = None,
        down_helix: Helix | None = None,
    ) -> None:
        """
        Initialize a double helix.

        Args:
            domain: The domain that the double helix is in.
            up_helix: The helix that progresses upwards from its 5' to 3' end. If
                None, a new and empty helix will be created.
            down_helix: The helix that progresses downwards from its 5' to 3' end. If
                None, a new and empty helix will be created.
        """
        self.domain = domain
        self.helices = (
            up_helix or Helix(direction=UP, size=None, double_helix=self),
            down_helix or Helix(direction=DOWN, size=None, double_helix=self),
        )

        # The helices must contain empty arrays of the size that the Domains indicates.
        self.left_helix.data.resize(self.domain.left_helix_count)
        self.other_helix.data.resize(self.domain.other_helix_count)

    @property
    def left_helix(self) -> Helix:
        """
        The helix that is on the left side of the domain and is thus lined up with
        the previous domain's right helical joint.
        """
        return self.helices[self.domain.left_helix_joint]

    @property
    def right_helix(self) -> Helix:
        """
        The helix that is on the right side of the domain and is thus lined up with the
        next domain's left helical joint.
        """
        return self.helices[self.domain.right_helix_joint]

    @property
    def up_helix(self) -> Helix:
        """
        The helix that has progresses upwards from its 5' to 3' ends.
        """
        return self.helices[UP]

    @property
    def down_helix(self) -> Helix:
        """
        The helix that has progresses downwards from its 5' to 3' ends.
        """
        return self.helices[DOWN]

    @property
    def zeroed_helix(self) -> Helix:
        """
        The helix that is lined up with the previous double helix on the left side.
        """
        return self.helices[self.domain.left_helix_joint]

    @property
    def other_helix(self) -> Helix:
        """
        The other helix in the same domain as the zeroed helix.
        """
        return self.helices[inverse(self.domain.left_helix_joint)]
