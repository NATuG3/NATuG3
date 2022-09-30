import pickle
import logging
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from dataclasses import dataclass
from typing import Union


filename = "settings.nano"
current = None  # current profile
profiles = None  # all profiles
logger = logging.getLogger(__name__)


@dataclass
class profile:
    """
    A settings profile.

    Attributes:
        D (float): Diameter of a domain.
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

    D: float = 0
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


def load():
    global current
    global profiles

    try:
        logger.debug("Settings file found. Loading setting profiles...")
        # attempt to open the settings file, or create a new settings file with
        # DNA-B settings (as a default/example)
        with open(filename, "rb") as settings_file:
            current, profiles = pickle.load(settings_file)

    except FileNotFoundError:
        logger.debug("Settings file not found. Restoring defaults...")
        current = profile(
            D=2.2,
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


def dump():
    """Dump persisting attributes of this module to a file"""
    # dump settings to file in format current-profile, all-profiles
    with open(filename, "wb") as settings_file:
        pickle.dump((current, profiles), settings_file)


class widget(QWidget):
    """Nucleic Acid Config Tab"""

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("config/ui/nucleic_acid.ui", self)

        def update_current():
            """
            Update config.nucleic_acid.current with current settings.

            Runs whenever an input box in the nucleic_acid panel is changed.
            """
            global current
            current = self.fetch_profile()

        # restore the current settinsg
        self.dump_profile(current)

        # if the value of any input is changed update nucliec_acid.current
        # (to match new settings)
        self.D.valueChanged.connect(update_current)
        self.H.valueChanged.connect(update_current)
        self.T.valueChanged.connect(update_current)
        self.B.valueChanged.connect(update_current)
        self.Z_c.valueChanged.connect(update_current)
        self.Z_s.valueChanged.connect(update_current)
        self.Z_b.valueChanged.connect(update_current)
        self.theta_b.valueChanged.connect(update_current)
        self.theta_c.valueChanged.connect(update_current)
        self.theta_s.valueChanged.connect(update_current)

    def dump_profile(self, profile: profile):
        """Saves current settings to profile with name in text edit input box."""
        self.D.setValue(profile.D)
        self.H.setValue(profile.H)
        self.T.setValue(profile.T)
        self.B.setValue(profile.B)
        self.Z_c.setValue(profile.Z_c)
        self.Z_s.setValue(profile.Z_s)
        self.Z_b.setValue(profile.Z_b)
        self.theta_b.setValue(profile.theta_b)
        self.theta_c.setValue(profile.theta_c)
        self.theta_s.setValue(profile.theta_s)

    def fetch_profile(self):
        """Fetch a profile object with all current nucleic acid settings from inputs."""
        return profile(
            D=self.D.value(),
            H=self.H.value(),
            T=self.T.value(),
            B=self.B.value(),
            Z_c=self.Z_c.value(),
            Z_s=self.Z_s.value(),
            Z_b=self.Z_b.value(),
            theta_b=self.theta_b.value(),
            theta_c=self.theta_c.value(),
            theta_s=self.theta_s.value(),
        )
