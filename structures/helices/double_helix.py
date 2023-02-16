from constants.directions import DOWN, UP
from structures.strands import Strand
from utils import inverse


class DoubleHelix:
    """
    A container storing the two strands of a double helix.

    Though this class is initialized and directly stores helices based off of their
    upwardness/downwardness, they are able to easily be accessed in many ways. See
    attributes for more information.

    Attributes:
        zeroed_strand: The strand that is lined up with the previous double helix on
            the left side.
        other_strand: The other strand in the same domain as the zeroed strand.
        up_strand: The strand that has progresses upwards from its 5' to 3' ends.
        down_strand: The strand that has progresses downwards from its 5' to 3' ends.
        left_helix: The helix that is on the left side of the domain and is thus
            lined up with the previous domain's right helical joint.
        right_helix: The helix that is on the right side of the domain and is thus
            lined up with the next domain's left helical joint.
    """

    __slots__ = "domain", "strands"

    def __init__(
        self,
        domain: "Domain",
        up_helix: Strand | None = None,
        down_helix: Strand | None = None,
    ) -> None:
        """
        Initialize a double helix.

        Args:
            domain: The domain that the double helix is in.
            up_helix: The strand that progresses upwards from its 5' to 3' ends. If
                this is None then an empty strand will be created.
            down_helix: The strand that progresses downwards from its 5' to 3' ends.
                If this is None then an empty strand will be created.
        """
        self.domain = domain
        self.strands = (
            up_helix if up_helix is not None else Strand(),
            down_helix if down_helix is not None else Strand(),
        )
        self.up_helix.direction = UP
        self.down_helix.direction = DOWN

    def __getitem__(self, item):
        if item in (DOWN, UP):
            return self.strands[item]

    def __iter__(self):
        return iter(self.strands)

    def assign_metadata(self):
        """
        Assign the domain and direction of each item in both strands of the double helix.

        This method iterates through the up and down strand, and then iterates through
        the items, setting each item's .domain and .direction attributes to the strand's
        domain and direction, respectively.
        """
        for item in self.up_helix:
            item.domain = self.domain
            item.direction = UP
        for item in self.down_helix:
            item.domain = self.domain
            item.direction = DOWN

    @property
    def left_helix(self) -> Strand:
        """
        The helix that is on the left side of the domain and is thus lined up with
        the previous domain's right helical joint.
        """
        return self.strands[self.domain.left_helix_joint]

    @property
    def right_helix(self) -> Strand:
        """
        The helix that is on the right side of the domain and is thus lined up with the
        next domain's left helical joint.
        """
        return self.strands[self.domain.right_helix_joint]

    @property
    def up_helix(self) -> Strand:
        """
        The strand that has progresses upwards from its 5' to 3' ends.
        """
        return self.strands[0]

    @property
    def down_helix(self) -> Strand:
        """
        The strand that has progresses downwards from its 5' to 3' ends.
        """
        return self.strands[1]

    @property
    def zeroed_helix(self) -> Strand:
        """
        The strand that is lined up with the previous double helix on the left side.
        """
        return self.strands[self.domain.left_helix_joint]

    @property
    def other_helix(self) -> Strand:
        """
        The other strand in the same domain as the zeroed strand.
        """
        return self.strands[inverse(self.domain.left_helix_joint)]
