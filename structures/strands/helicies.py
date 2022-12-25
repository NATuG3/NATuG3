from dataclasses import dataclass, field
from typing import List

from constants.directions import DOWN, UP
from structures.domains import Domain
from structures.strands import Strand


@dataclass(slots=True)
class DoubleHelix:
    """
    A container for storing datapoints before converting them into strands.

    When creating strands from a list of domains we use numpy arrays to store the
    angles, x coords, and y coords. We place the numpy arrays by domain and by zeroed/
    other strand into larger lists for easy access; however, we want to also be able
    to access them directly by direction.

    To access a strand by direction, use the by_direction(direction) method.
    To access the zeroed strand, use the zeroed_strand attribute.
    To access the other strand, use the other_strand attribute.

    Attributes:
        zeroed_strand: The strand that is of the direction of self.domain's left
            helix joint
        other_strand: The other strand in the same helix as the zeroed strand.
        up_strand: The strand that is of the UP direction.
        down_strand: The strand that is of the DOWN direction.
        left_helix: The helix that is on the left side of the domain.
        right_helix: The helix that is on the right side of the domain.

    Methods:
        by_direction(direction): Returns the strand that is of the direction provided.
    """

    domain: Domain
    container: type = Strand
    zeroed_strand: object = None
    other_strand: object = None

    def __post_init__(self):
        """
        If the zeroed strand is not provided, create it using the user provided
        container, or the default container (Strand).
        """
        if self.zeroed_strand is None:
            self.zeroed_strand = self.container()
        if self.other_strand is None:
            self.other_strand = self.container()

    def by_direction(self, direction):
        """
        Returns the strand that is of the direction provided.

        Args:
            direction: The direction of the strand to return.

        Returns:
            The strand that is of the direction provided.
        """
        if self.domain.left_helix_joint == direction:
            return self.zeroed_strand
        else:
            return self.other_strand

    @property
    def up_strand(self):
        """Returns the strand that is of the UP direction."""
        return self.by_direction(UP)

    @property
    def down_strand(self):
        """Returns the strand that is of the DOWN direction."""
        return self.by_direction(DOWN)

    @property
    def left_helix(self):
        """Returns the left helix of the domain."""
        return self.by_direction(self.domain.left_helix_joint)

    @property
    def right_helix(self):
        """Returns the right helix of the domain."""
        return self.by_direction(self.domain.left_helix_joint)
