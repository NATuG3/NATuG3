from constants.directions import *
from structures.profiles import NucleicAcidProfile
from structures.strands import Strand


class Domain:
    """
    A singular domain object.

    Attributes:
        parent: The parent workers container object. If this is None then index becomes None too.
        index: The index of this domain in its parent.
        left_helix_joint: The left helix joint's upwardness or downwardness.
            "Left" indicates that the left side of this domain will be lined up to
            the right helix joint of the previous domain. Uses the constant 0 for up and 1 for down.
        right_helix_joint: The right helix joint's upwardness or downwardness.
            "right" indicates that the right side of this domain will be lined up to
            the left helix joint of the next domain. Uses the constant 0 for up and 1 for down.
        up_strand (Strand): The up strand of the domain. This is an unparented strand object.
        down_strand (Strand): The down strand of the domain. This is an unparented strand object.
        theta_m_multiple: Angle between this and the next workers' line of tangency. Multiple of theta_c.
            This is the angle between i,i+1's line of tangency and i+1,i+2's line of tangency
            where i is the index of this domain.
            This is the theta_m_multiple times the characteristic angle.
        theta_m: Angle between this and the next workers' line of tangency. In degrees.
            This is the angle between i,i+1's line of tangency and i+1,i+2's line of tangency
            where i is the index of this domain.
            This is the theta_m_multiple times the characteristic angle.
        theta_s_multiple: The switch from upness to downness (or lack thereof) of the helix joints.
            (-1) for up to down switch; (0) for both up/down switch; (1) for down to up switch
        theta_s: The switch angle for the transition between an up and down strand (or 0 if there is none).
            This is the theta_s_multiple times the characteristic angle.
        nucleic_acid_profile: the nucleic acid configuration for the domain.
        count: Number of initial NEMids/strand to generate.
    """

    def __init__(
        self,
        nucleic_acid_profile: NucleicAcidProfile,
        theta_m_multiple: int,
        left_helix_joint_direction: int,
        right_helix_joint_direction: int,
        count: int,
        parent: "Domains" = None,
        index: int = None,
    ):
        """
        Initialize a Domain object.

        Args:
            nucleic_acid_profile: The nucleic acid settings profile
            theta_m_multiple: Angle between this and the next workers' lines of tangency. Multiple of theta c.
            left_helix_joint_direction: The left helix joint's direction.
            right_helix_joint_direction: The right helix joint's direction.
            count: Number of initial NEMids/strand to generate.
            parent (Subunit): The parent subunit. Defaults to None.
            index (int): The index of this domain in its parent. Defaults to None.
        """
        # store the parent subunit
        self.parent = parent

        # store the nucleic acid settings
        self.nucleic_acid_profile = nucleic_acid_profile

        # multiple of the characteristic angle (theta_c) for the interior angle
        self.theta_interior_multiple: int = theta_m_multiple

        # the helical joints
        self.left_helix_joint = left_helix_joint_direction
        self.right_helix_joint = right_helix_joint_direction

        # store the number of initial NEMids/strand to generate
        self.count = count

        # set the index of the domain
        self.index = index

    @property
    def left_strand(self) -> Strand | None:
        """
        The left strand of the domain.

        The grandparent's .points() method is used to obtain the strand. Note that the grandparent
        of a Domain object is the parent of the parent. The parent of a Domains object is a Subunit object,
        and the parent of a Subunit object is a Domains object. It is the Domains object that has a .points()
        method.

        Returns:
            The left strand of the domain or None if the domain doesn't have a parent.
        """
        if self.parent is None or self.parent.parent:
            return None
        else:
            return Strand(self.parent.parent.points()[self.index][RIGHT])

    @property
    def right_strand(self) -> Strand | None:
        """
        The right strand of the domain.

        The grandparent's .points() method is used to obtain the strand. Note that the grandparent
        of a Domain object is the parent of the parent. The parent of a Domains object is a Subunit object,
        and the parent of a Subunit object is a Domains object. It is the Domains object that has a .points()
        method.

        Returns:
            The right strand of the domain or None if the domain doesn't have a parent.
        """
        if self.parent is None:
            return None
        else:
            return Strand(self.parent.parent.points()[self.index][RIGHT])

    def __setattr__(self, key, value):
        """Set the attribute and update the parent if necessary."""
        # set the attribute
        super().__setattr__(key, value)
        # then update parent
        if key != "parent" and self.parent is not None:
            # if there is a parent make sure to clear its strands cache
            # so that the strands of all workers can be recomputed
            if self.parent is not None:
                self.parent.parent.domains.cache_clear()
                self.parent.parent.subunits.cache_clear()

    @property
    def theta_s_multiple(self) -> int:
        """
        Obtain the theta switch multiple. This is either -1, 0, or 1.
        Based on the left and right helical joints, this outputs:
        (-1) for up to down; (0) for both up/down; (1) for down to up

        This is very computationally inexpensive, so it is a property. (self.theta_s_multiple)
        """
        helix_joints = (
            self.left_helix_joint,
            self.right_helix_joint,
        )
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
        """
        Obtain the theta switch angle.

        This is equivalent to self.theta_s_multiple * self.theta_c.
        """
        return self.theta_s_multiple * self.nucleic_acid_profile.theta_s

    @property
    def theta_m(self) -> float:
        """
        Obtain the theta interior angle.

        This is equivalent to self.theta_interior_multiple * self.theta_c.
        """
        return self.theta_interior_multiple * self.nucleic_acid_profile.theta_c
