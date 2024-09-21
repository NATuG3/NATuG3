from copy import copy
from typing import Tuple
from uuid import uuid1

from natug.constants.directions import *
from natug.structures.points.point import x_coord_from_angle
from natug.structures.profiles import NucleicAcidProfile
from natug.structures.strands import Strand
from natug.utils import inverse


class GenerationCount:
    """
    A class for storing the number of NEMids to generate for a domain.

    Attributes:
        bottom_count: The number of NEMids to generate for the bottom strand.
        body_count: The number of NEMids to generate for the body strand.
        top_count: The number of NEMids to generate for the top strand.

    Method:
        direction: The direction that this is the generation count for.
    """

    def __init__(self, count: Tuple[int, int, int], direction=None):
        """
        Initialize a GenerationCount object.

        Args:
            count: The number of NEMids to generate for the bottom, body, and top
                strands.
        """
        self.bottom_count = count[0]
        self.body_count = count[1]
        self.top_count = count[2]

        self.direction = direction

    def __len__(self) -> int:
        """
        Get the number of NEMids to generate for the bottom, body, and top strands.

        Returns:
            The number of NEMids to generate for the bottom, body, and top strands.
        """
        return 3

    def __getitem__(self, index: int) -> int:
        """
        Get the number of NEMids to generate for the bottom, body, and top strands.

        Args:
            index: The index of the number of NEMids to generate for the bottom, body,
                and top strands.

        Returns:
            The number of NEMids to generate for the bottom, body, and top strands.
        """
        if index == 0:
            return self.bottom_count
        elif index == 1:
            return self.body_count
        elif index == 2:
            return self.top_count
        else:
            raise IndexError("Index out of range.")

    def __setitem__(self, index: int, value: int):
        """
        Set the number of NEMids to generate for the bottom, body, and top strands.

        Args:
            index: The index of the number of NEMids to generate for the bottom, body,
                and top strands.
            value: The number of NEMids to generate for the bottom, body, and top
                strands.
        """
        if index == 0:
            self.bottom_count = value
        elif index == 1:
            self.body_count = value
        elif index == 2:
            self.top_count = value
        else:
            raise IndexError("Index out of range.")

    def __repr__(self):
        return f"GenCount({self.bottom_count}, {self.body_count}, {self.top_count})"

    def to_str(self):
        """
        Get a string representation of the generation count.

        Returns:
            A string representation of the generation count of the form:
            "bottom_count-body_count-top_count"
        """
        return f"{self.bottom_count}-{self.body_count}-{self.top_count}"

    @classmethod
    def from_str(cls, string: str):
        """
        Get a GenerationCount object from a string representation of the generation
        count.

        Args:
            string: A string representation of the generation count of the form:
                "bottom_count-body_count-top_count"
        """
        count = string.split("-")
        return cls((int(count[0]), int(count[1]), int(count[2])))


class Domain:
    """
    A singular domain object.

    Attributes:
        parent: The Subunit container object containing the Domain. Domains live in
            Subunits, which live in Domains.
        index: The index of this domain in its Subunit's Domain's object. Index-0.
        theta_m_multiple: Number of characteristic angles (NucleicAcidProfile.theta_c-s)
            between this and the next domains' line of tangency, not taking into account
            any switches.
        theta_m: The actual angle between this and the next domains' line of tangency, in
            degrees, not taking into account any switches.
        theta_s_multiple: The switch from upness to downness (or lack thereof) of the
            helix joints. (-1) for up to down switch; (0) for both up/down switch; (1)
            for down to up switch.
        theta_s: The actual angle of the switch from upness to downness (or lack thereof),
            in degrees.
        theta_i: The angle between this domain and the next domain's line of
            tangency, in degrees, taking into account any switches.
        theta_e: The exterior angle between this domain and the next domain's line of
            tangency. Equal to 360 - theta_i.
        nucleic_acid_profile: the nucleic acid configuration for the domain.
        left_helix_joint: The left helix joint's upwardness or downwardness.
            "Left" indicates that the left side of this domain will be lined up to
            the right helix joint of the previous domain. Uses the constant 0 for up and
            1 for down.
        right_helix_joint: The right helix joint's upwardness or downwardness.
            "right" indicates that the right side of this domain will be lined up to
            the left helix joint of the next domain. Uses the constant 0 for up and 1
            for down.
        up_helix_count (GenerationCount): The number of nucleosides to initially
            generate for the up helix of the domain.
        down_helix_count (GenerationCount): The number of nucleosides to initially
            generate for the up helix of the domain.
        uuid: The unique identifier for the domain. This is automatically generated.

    Methods:
        inverted: A domain with helix joint directions that are the inverse of what they
            were normally.
    """

    def __init__(
        self,
        nucleic_acid_profile: NucleicAcidProfile,
        theta_m_multiple: int,
        left_helix_joint: int,
        right_helix_joint: int,
        up_helix_count: Tuple[int, int, int],
        down_helix_count: Tuple[int, int, int],
        parent: "Domains" = None,
        index: int = None,
        uuid: str = None,
    ):
        """
        Initialize a Domain object.

        Args:
            nucleic_acid_profile: The nucleic acid settings nucleic_acid_profile
            theta_m_multiple: Angle between this and the next workers' lines of
                tangency. Multiple of theta c.
            left_helix_joint: The left helix joint's upwardness or downwardness.
                "Left" indicates that the left side of this domain will be lined up to
                the right helix joint of the previous domain. Uses the constant 0 for
                up and 1 for down.
            right_helix_joint: The right helix joint's upwardness or downwardness.
                "right" indicates that the right side of this domain will be lined up to
                the left helix joint of the next domain. Uses the constant 0 for up and
                1 for down.
            up_helix_count: The number of nucleosides to initially
                generate for the up helix of the domain. This should be passed as a
                tuple of three integers, and will be converted to a GenerationCount
                object.
            down_helix_count: The number of nucleosides to initially
                generate for the up helix of the domain. This should be passed as a
                tuple of three integers, and will be converted to a GenerationCount
                object.
            parent (Subunit): The strands subunit. Defaults to None.
            index (int): The index of this domain in its strands. Defaults to None.
            uuid (str): The unique identifier for the domain. This is automatically
                generated. Defaults to None.
        """
        # store the strands subunit
        self.parent = parent

        # store the nucleic acid settings
        self.nucleic_acid_profile = nucleic_acid_profile

        # multiple of the characteristic angle (theta_c) for the interior angle
        self.theta_m_multiple: int = theta_m_multiple

        # the helical joints
        self.left_helix_joint = left_helix_joint
        self.right_helix_joint = right_helix_joint
        assert self.left_helix_joint in [0, 1]
        assert self.right_helix_joint in [0, 1]

        # the number of NEMids to generate for the left and right helices
        self.up_helix_count = GenerationCount(
            up_helix_count, direction=lambda: self.left_helix_joint
        )
        self.down_helix_count = GenerationCount(
            down_helix_count, direction=lambda: self.right_helix_joint
        )

        # set the index of the domain
        self.index = index

        # set the uuid
        self.uuid = uuid or str(uuid1())

    def __sub__(self, other):
        """
        Subtract two domains indices.

        Args:
            other: The other domain to subtract from this one.

        Returns:
            The difference between the two domains' indices.
        """
        return self.index - other.index

    def __add__(self, other):
        """
        Add two domains indices.

        Args:
            other: The other domain to add to this one.

        Returns:
            The sum of the two domains' indices.
        """
        return self.index + other.index

    def __eq__(self, other):
        """
        Check if two domains are equal by comparing their indices within the global
        domain object.

        Args:
            other: The other domain to check for equality.

        Returns:
            True if the domains are equal, False otherwise.
        """
        return isinstance(other, Domain) and self.index == other.index

    def inverted(self):
        """A domain with inverted helix joint directions."""
        output = copy(self)
        output.left_helix_joint = inverse(self.left_helix_joint)
        output.right_helix_joint = inverse(self.right_helix_joint)
        return output

    def angles(self, start=0):
        """
        Obtain the angles of the NEMids of the Domain.

        Yields:
            The angle of each NEMid in the domain.
        """
        angle = start
        while True:
            angle += self.nucleic_acid_profile.theta_b
            yield angle

    def x_coords(self):
        """
        Obtain the x coords of the NEMids of the Domain.

        Yields:
            The x coords of each NEMid in the domain.
        """
        for angle in self.angles():
            yield x_coord_from_angle(angle, self)

    def z_coords(self, start=0):
        """
        Obtain the z coords of the NEMids of the Domain.

        Yields:
            The z coords of each NEMid in the domain.
        """
        z_coord = start
        while True:
            z_coord += self.nucleic_acid_profile.Z_b
            yield z_coord

    @property
    def left_strand(self) -> Strand | None:
        """
        The left strand of the domain.

        The grandparent's .points() method is used to obtain the strand. Note that
        the grandparent of a Domain object is the strands of the strands. The strands of
        a Domains object is a Subunit object, and the strands of a Subunit object is a
        Domains object. It is the Domains object that has a .points() method.

        Returns:
            The left strand of the domain or None if the domain doesn't have a strands.
        """
        if self.parent is None or self.parent.strands:
            return None
        else:
            return Strand(self.parent.strands.items()[self.index][RIGHT])

    @property
    def right_strand(self) -> Strand | None:
        """
        The right strand of the domain.

        The grandparent's .points() method is used to obtain the strand. Note that
        the grandparent of a Domain object is the strands of the strands. The strands of
        a Domains object is a Subunit object, and the strands of a Subunit object is a
        Domains object. It is the Domains object that has a .points() method.

        Returns:
            The right strand of the domain or None if the domain doesn't have a strands.
        """
        if self.parent is None:
            return None
        else:
            return Strand(self.parent.strands.items()[self.index][RIGHT])

    @property
    def theta_s_multiple(self) -> int:
        """
        Obtain the theta switch multiple. This is either -1, 0, or 1.
        Based on the left and right helical joints, this outputs:
        (-1) for up to down; (0) for both up/down; (1) for down to up

        This is very computationally inexpensive, so it is a property.
        (self.theta_s_multiple)
        """
        try:
            return {
                (UP, DOWN): -1,
                (UP, UP): 0,
                (DOWN, DOWN): 0,
                (DOWN, UP): 1,
            }[(self.left_helix_joint, self.right_helix_joint)]
        except KeyError:
            raise ValueError(
                "Invalid helical joint integer",
                (self.left_helix_joint, self.right_helix_joint),
            )

    @property
    def theta_s(self) -> float:
        """
        Obtain the theta switch angle.

        This is equivalent to self.theta_s_multiple * self.theta_s.
        Updated Bill 2/11/23
        """
        return self.theta_s_multiple * self.nucleic_acid_profile.theta_s

    @property
    def theta_m(self) -> float:
        """
        Obtain the theta interior angle.

        This is equivalent to self.theta_m_multiple * self.theta_c.
        """
        return self.theta_m_multiple * self.nucleic_acid_profile.theta_c

    @property
    def theta_i(self) -> float:
        """
        Obtain the theta interior angle.

        This is equivalent to self.theta_m + self.theta_s.
        """
        return self.theta_m + self.theta_s

    @property
    def theta_e(self) -> float:
        """
        Obtain the theta exterior angle.

        This is equivalent to 360 - self.theta_i.
        """
        return 360 - self.theta_i

    def __repr__(self):
        """Return a string representation of the Domain object."""
        return (
            f"Domain("
            f"m={self.theta_m_multiple}, "
            f"left_joint={self.left_helix_joint}, "
            f"right_joint={self.right_helix_joint}, "
            f"up_count={self.up_helix_count}, "
            f"down_count={self.down_helix_count}, "
            f"index={self.index}"
            f")"
        )
