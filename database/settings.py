import pickle
from dataclasses import dataclass
from typing import Union
import logging


filename = "settings.nano"
logger = logging.getLogger(__name__)


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


def refresh():
    """
    Refresh the settings variable with the current user-inputted settings.

    Grabs data from actual UI.
    """
    pass


def dump():
    """Dump persisting attributes of this module to a file"""
    # dump settings to file in format current-profile, all-profiles
    with open(filename, "wb") as settings_file:
        pickle.dump((current, profiles), settings_file)


def load():
    """Load persisting attributes of this module from a file"""
    global profiles  # settings.profiles is global
    global current  # settings.current is global

    try:
        logger.debug("Settings file found. Loading setting profiles...")
        # attempt to open the settings file, or create a new settings file with
        # DNA-B settings (as a default/example)
        with open(filename, "rb") as settings_file:
            current, profiles = pickle.load(settings_file)
    except FileNotFoundError:
        logger.debug("Settings file not found. Restoring defaults...")
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
        profiles = {"B-DNA": current}

    logger.debug("Loaded profiles.")
    logger.debug(profiles)
