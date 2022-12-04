from typing import Tuple, Literal

from constants.directions import *
from structures.profiles import NucleicAcidProfile
from structures.strands import Strand


class Domain:
    """
    Domain storage object.
    Attributes:
        index: The index of the domain.
        left_helix_joint_direction: The left helix joint's upwardness or downwardness.
        right_helix_joint_direction: The right helix joint's upwardness or downwardness.
        up_strand: The up strand of the domain.
        down_strand: The down strand of the domain.
        theta_m_multiple: Angle between this and the next domains' line of tangency. Multiple of theta_c.
        theta_m: Angle between this and the next domains' line of tangency.
        theta_s_multiple: The switch from upness to downness (or lack thereof) of the helix joints.
        theta_s: The switch angle for the transition between an up and down strand (or 0 if there is none).
        helix_joints: The upwardness/downwardness of the left and right helix joint.
        nucleic_acid_profile: the nucleic acid configuration for the domain.
    """

    def __init__(
        self,
        nucleic_acid_profile: NucleicAcidProfile,
        index: int,
        theta_m_multiple: int,
        left_helix_joint_direction: int,
        right_helix_joint_direction: int,
        count: int,
    ):
        """
        Initialize a Domain object.
        Args:
            nucleic_acid_profile: The nucleic acid settings profile
            index: The index of the domain.
            theta_m_multiple: Angle between this and the next domains' lines of tangency. Multiple of theta c.
            left_helix_joint_direction: The left helix joint's direction.
            right_helix_joint_direction: The right helix joint's direction.
            count: Number of initial NEMids/strand to generate.
        """
        # store the nucleic acid settings
        self.nucleic_acid_profile = nucleic_acid_profile

        # multiple of the characteristic angle (theta_c) for the interior angle
        self.index = index
        self.theta_interior_multiple: int = theta_m_multiple

        # the helical joints
        self.left_helix_joint_direction = left_helix_joint_direction
        self.right_helix_joint_direction = right_helix_joint_direction

        # store the number of initial NEMids/strand to generate
        self.count = count

        # create containers to store the domain's containers
        self.left_strand = Strand(self.nucleic_acid_profile)
        self.right_strand = Strand(self.nucleic_acid_profile)

    @property
    def theta_s_multiple(self) -> Literal[-1, 0, 1]:
        """
        Obtain the theta switch multiple. This is either -1, 0, or 1.
        Based on the left and right helical joints, this outputs:
        (-1) for up to down; (0) for both up/down; (1) for down to up
        """
        helix_joints = (self.left_helix_joint_direction, self.right_helix_joint_direction,)
        if helix_joints == (UP, DOWN):
            return -1
        elif helix_joints == (UP, UP):
            return 0
        elif helix_joints == (DOWN, DOWN):
            return 0
        elif helix_joints == (DOWN, UP):
            return 1
        else:
            raise ValueError("Invalid helical joint integer", helix_joints)

    @property
    def theta_s(self) -> float:
        """Obtain the theta switch angle."""
        return self.theta_s_multiple * self.nucleic_acid_profile.theta_s

    @property
    def theta_m(self) -> float:
        """Obtain the theta interior angle."""
        return self.theta_interior_multiple * self.nucleic_acid_profile.theta_c

    def __eq__(self, other) -> bool:
        """Whether us.index == them.index."""
        if not isinstance(other, type(self)):
            return False
        return self.index == other.index

    def __repr__(self) -> str:
        return (
            f"domain("
            f"index={self.index}, "
            f"Θ_interior_multiple={self.theta_interior_multiple}, "
            f"helix_joints=(left={self.left_helix_joint_direction}, "
            f"right={self.right_helix_joint_direction}), "
            f"Θ_switch_multiple={self.theta_s_multiple}"
            f")"
        )