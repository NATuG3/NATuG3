from typing import Tuple, Literal

from constants.directions import *


class Domain:
    """
    Domain storage object.

    Attributes:
        index (int): THe index of the domain.
        theta_interior (int): Angle between domain #i/#i+1's & #i+1/i+2's tangency lines. Multiple of theta_c.
        theta_switch_multiple (int): Strand switch angle per domain transition. Multiple of theta_s.
        helix_joints (tuple): The upwardness/downwardness of the left and right helix joint.
    """

    def __init__(
            self,
            index,
            theta_interior_multiple: int,
            helix_joints: Tuple[Literal[UP, DOWN], Literal[UP, DOWN]],
            count: int,
    ):
        """
        Create domains dataclass.

        Args:
            index (int): THe index of the domain.
            theta_interior_multiple:
                Angle between domain #i/#i+1's and #i+1/i+2's lines of tangency.
                Multiple of characteristic angle.
            helix_joints (tuple): (left_joint, right_joint) where left/right_joint are constants.directions.UP/DOWN.
            count (int): Number of initial NEMids/strand to generate.
        """
        # multiple of the characteristic angle (theta_c) for the interior angle
        self.index = index
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

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.index == other.index

    def __repr__(self) -> str:
        return (
            f"domain("
            f"index={self.index}, "
            f"Θ_interior_multiple={self.theta_interior_multiple}, "
            f"helix_joints=(left={self.helix_joints[LEFT]}, "
            f"right={self.helix_joints[RIGHT]}), "
            f"Θ_switch_multiple={self.theta_switch_multiple}"
            f")"
        )
