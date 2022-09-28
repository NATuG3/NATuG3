from dataclasses import dataclass
from multiprocessing.sharedctypes import Value
from typing import Literal, Tuple, Union, Tuple


@dataclass
class profile:
    """
    A settings profile.
    Attributes:
        count (int): Number of NEMids to initially generate per strand.
        diameter (float): Diameter of a domain.
        H (float): Height of a turn.
        T (float): There are T turns every B bases.
        B (float): There are B bases every T turns.
        Z_c (float): Characteristic height.
        Z_s (float): Switch height.
        Z_b (float): Base height.
        theta_b (float): Base angle.
        theta_c (float): Characteristic angle.
        theta_s (float): Switch angle.
    """

    count: int = 300
    diameter: float = 0
    H: float = 0.0
    T: int = 0
    B: int = 0
    Z_c: float = 0.0
    Z_b: Union[float, None] = None
    Z_s: float = 0.0
    theta_b: float = 0.0
    theta_c: float = 0.0
    theta_s: float = 0.0

    def __post_init__(self):
        # if self.Z_b isn't set then compute it
        if self.Z_b is None:
            self.Z_b = (self.T * self.H) / self.B
            self.Z_b = round(self.Z_b, 5)


@dataclass
class domain:
    """
    Domain storage object.
    Attributes:
        theta_interior (int): The angle between domain #i/#i+1's line of tangency and domain #i+1/i+2's line of tangency
        switch_angle_multiple (int): Strand switch angle per domain transition. Integer multiple of strand switch angle.
    """

    # multiple of the characteristic angle (theta_c) for the interior angle 
    # between this domains[this domain's index] and this domains[this domain's index + 1]
    theta_interior_multiple: int

    # indicates that the left helix joint to right helix joint goes...
    # (-1) up to down; (0) both up/down; (1) down to up
    #
    # this does not need to be defined if theta_switch_multiple is defined
    theta_switch_multiple: Literal[-1, 0, 1] = None

    # [left_helix_joint, right_helix_joint]
    # where left_helix_joint and right_helix_joint
    # are either 0 (up) or 1 (down)
    # for example...
    # [0, 1] means that the left helix joint is upwards/right helix joint is downwards
    #
    # this does not need to be defined if theta_switch_multiple is -1 or 1
    helix_joints: Tuple[Literal[0, 1], Literal[0, 1]] = None


@dataclass
class NEMid:
    """Dataclass for a NEMid."""

    # Generic Attributes
    x_coord: float
    z_coord: float
    angle: float

    # NEMid Specific Attributes
    is_junction: bool = False

    def __repr__(self) -> str:
        return f"NEMid(pos={self.position()}), angle={round(self.angle, 3)}°, is_junction={str(self.is_junction).lower()}"

    def position(self, round_to=3) -> Tuple[float, float]:
        """Return coords of the NEMid as a tuple of form (x, z)"""
        return (round(self.x_coord, round_to), round(self.z_coord, round_to))


@dataclass
class nucleoside:
    """Dataclass for a nucleoside."""

    # Generic Attributes
    x_coord: float
    z_coord: float
    angle: float

    # Base Specific Attributes
    base: Literal["A", "T", "G", "C", "U", None]

    def __repr__(self) -> str:
        return f"base(pos={self.position()}), angle={round(self.angle, 3)}°, base={str(self.base).replace('None','unset')}"

    def position(self, round_to=3) -> Tuple[float, float]:
        """Return coords of the base as a tuple of form (x, z)"""
        return (round(self.x_coord, round_to), round(self.z_coord, round_to))

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
