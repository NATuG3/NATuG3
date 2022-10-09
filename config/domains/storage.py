import logging
from dataclasses import dataclass
from typing import Tuple, Literal
from constants.directions import *
import pickle
import atexit

restored_filename = "config/domains/restored.nano"
current = None

logger = logging.getLogger(__name__)


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
        # between this domains[this domain's index] and this domains[this domain's index + 1]
        self.theta_interior_multiple: int = theta_interior_multiple

        # the left and right helical joints
        # constants.directions.left = 0
        # constants.directions.right = 1
        # so...
        # format is (left_joint, right_joint) where "left/right_joint" are constants.directions.UP/DOWN
        self.helix_joints: Tuple[Literal[UP, DOWN], Literal[UP, DOWN]] = helix_joints

        # store the number of initial NEMids/strand to generate
        self.count = count

        # theta_switch_multiple
        # indicates that the left helix joint to right helix joint goes either...
        # (-1) up to down; (0) both up/down; (1) down to up
        #
        # this does not need to be defined if theta_switch_multiple is defined
        helix_joints = tuple(helix_joints) #ensure helix_joints is a tuple
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


def load():
    """Load the previous state of domains."""
    global current

    atexit.register(dump)

    try:
        with open(restored_filename, "rb") as restored_file:
            current = pickle.load(restored_file)
        logger.info("Restored previous domain editor state.")
    except FileNotFoundError:
        logger.info("Previous domain editor state save file not found. Loading defaults...")
        current = [Domain(9, (UP, UP), 50)] * 14


def dump():
    """Save current domains state for state restoration on load."""
    with open(restored_filename, "wb") as restored_file:
        # perform data validation before save
        for domain in current:
            if not isinstance(domain, Domain):
                raise TypeError("There is a domain in the domains list that is not a domain", domain)
        pickle.dump(current, restored_file)
