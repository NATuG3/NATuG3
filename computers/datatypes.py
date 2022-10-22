from dataclasses import dataclass
from types import NoneType
from typing import TypeVar
from typing import Tuple, Union, Literal

from constants import bases
from constants.directions import *


class Domain:
    """
    Domain storage object.

    Attributes:
        theta_interior (int): Angle between domain #i/#i+1's and #i+1/i+2's lines of tangency. Multiple of characteristic angle.
        theta_switch_multiple (int): Strand switch angle per domain transition. Multiple of strand switch angle.
        helix_joints (tuple): The upwardness/downwardness of the left and right helix joint.
    """

    def __init__(
            self,
            theta_interior_multiple: int,
            helix_joints: Tuple[Literal[UP, DOWN], Literal[UP, DOWN]],
            count: int,
    ):
        """
        Create domains dataclass.

        Args:
            theta_interior_multiple (int):
                Angle between domain #i/#i+1's and #i+1/i+2's lines of tangency. Multiple of characteristic angle.
            helix_joints (tuple):
                (left_joint, right_joint) where left/right_joint are constants.directions.UP/DOWN.
            count (int):
                Number of initial NEMids/strand to generate.
        """
        # multiple of the characteristic angle (theta_c) for the interior angle
        self.theta_interior_multiple: int = theta_interior_multiple

        # (left_joint, right_joint) where "left/right_joint" are constants.directions.UP/DOWN
        self.helix_joints: Tuple[Literal[UP, DOWN], Literal[UP, DOWN]] = helix_joints

        # store the number of initial NEMids/strand to generate
        self.count = count

        # (-1) up to down; (0) both up/down; (1) down to up
        # this does not need to be defined if theta_switch_multiple is defined
        helix_joints = tuple(helix_joints)  # ensure helix_joints is a tuple
        if helix_joints == (UP, DOWN):
            self.theta_switch_multiple = -1
        elif helix_joints == (UP, UP):
            self.theta_switch_multiple = 0
        elif helix_joints == (DOWN, DOWN):
            self.theta_switch_multiple = 0
        elif helix_joints == (DOWN, UP):
            self.theta_switch_multiple = 1
        else:
            raise ValueError("Invalid helical joint integer", helix_joints)

    def __repr__(self) -> str:
        return (
            f"domain("
            f"Θ_interior_multiple={self.theta_interior_multiple}, "
            f"helix_joints=(left={self.helix_joints[LEFT]}, "
            f"right={self.helix_joints[RIGHT]}, "
            f"Θ_switch_multiple={self.theta_switch_multiple}"
            f")"
        )


@dataclass
class NEMid:
    """
    NEMid object.

    Attributes:
        x_coord (float): The x coord of the NEMid.
        z_coord (float): The z coord of the NEMid.
        angle (float): Angle from this domain and next domains' line of tangency going counterclockwise.
        direction (Literal[UP, DOWN]): The direction of the helix at this NEMid.
        matching (NEMid): NEMid in same domain on other direction's helix across from this one.
        juncmate (Union[NEMid, None]): NEMid that can this NEMid can conjunct-with. NoneType if this no NEMid overlaps.
        junction (bool): Whether this NEMid is at the site of an active junction.
        junctable (bool): Whether this NEMid overlaps another NEMid and can thus can conjunct.
    """

    # Generic Attributes
    x_coord: float
    z_coord: float
    angle: float
    direction: Literal[UP, DOWN]
    matching: TypeVar = None

    # NEMid Specific Attributes
    juncmate: Union[TypeVar, NoneType] = None
    junction: bool = False
    junctable: bool = False


    @property
    def position(self) -> Tuple[float, float]:
        """Return coords of the base as a tuple of form (x, z)"""
        return self.x_coord, self.z_coord

    def __repr__(self) -> str:
        """Determine what to print when instance is printed directly."""
        return (
            f"NEMid("
            f"pos={tuple(map(lambda i: round(i, 3), self.position))}), "
            f"angle={round(self.angle, 3)}°, "
            f"junction={str(self.junction).lower()}, "
            f"junctable={str(self.junctable).lower()}"
        )


@dataclass
class Nucleoside:
    """Dataclass for a nucleoside."""

    # Generic Attributes
    x_coord: float
    z_coord: float
    angle: float

    # Base Specific Attributes
    base: Union[bases.A, bases.T, bases.G, bases.C, bases.U, NoneType]

    @property
    def position(self) -> Tuple[float, float]:
        """Return coords of the base as a tuple of form (x, z)"""
        return self.x_coord, self.z_coord

    def complementary_base(self) -> str:
        "Return the complement of this base"
        complements = {
            "A": "T",
            "T": "A",
            "U": "A",
            "A": "U",
            "C": "G",
            "G": "C",
        }
        return complements[self.nucleoside]

    def __repr__(self) -> str:
        return f"base(pos={self.position()}), angle={round(self.angle, 3)}°, base={str(self.base).replace('None', 'unset')}"

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return None
        try:
            if self.base == other.base:
                return True
        except AttributeError:
            return False
