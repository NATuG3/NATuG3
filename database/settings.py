import pickle
from types import SimpleNamespace
from dataclasses import dataclass
from typing import Union


filename = "settings.nano"

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
        if self.Z_b is None:
            self.Z_b = (self.T * self.H) / self.B


profiles = {}

current = profile(
    count=200,
    diameter=2.2,
    H=3.549,
    T=2,
    B=21,
    Z_c=0.17,
    Z_s=1.26,
    theta_b=34.29,
    theta_c=360 / 21,
    theta_s=2.3,
)


def refresh():
    """
    Refresh the settings variable with the current user-inputted settings.

    Grabs data from actual UI.
    """
    pass


def load():
    """Load persisting attributes of this module to a file"""
    storage = SimpleNamespace(
        current=current, profiles=profiles
    )  # store all variables in this container
    # dump settings to file
    with open(filename, "wb") as settings_file:
        pickle.dump(storage, settings_file)


def dump():
    """Dump persisting attributes of this module to a file"""
    storage = SimpleNamespace(
        current=current, profiles=profiles
    )  # store all variables in this container
    # dump settings to file
    with open(filename, "wb") as settings_file:
        pickle.dump(storage, settings_file)
