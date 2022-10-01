from contextlib import suppress
from dataclasses import dataclass
import logging
import pickle


profiles_filename = "config/nucleic_acid/profiles.nano"
restored_filename = "config/nucleic_acid/restored.nano"

current = None  # current profile
profiles = None  # all profiles
previous_profile_name = None  # name of previously loaded profile


# set up logger
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
    Z_s: float = 0.0
    theta_b: float = 0.0
    theta_c: float = 0.0
    theta_s: float = 0.0

    def __post_init__(self) -> None:
        # compute Z_b based on T, H, and B
        self.Z_b = (self.T * self.H) / self.B
        self.Z_b = round(self.Z_b, 4)

    def __eq__(self, other: object) -> bool:
        """Returns true if identical profile is returned"""
        return vars(self) == vars(other)


def load() -> None:
    global current
    global previous_profile_name
    global profiles

    # attempt to load the nucleic acid settings file
    try:
        logger.debug("Settings file found. Loading setting profiles...")
        # attempt to open the settings file, or create a new settings file with
        # DNA-B settings (as a default/example)
        with open(profiles_filename, "rb") as settings_file:
            profiles = pickle.load(settings_file)

        # if profile dict was empty then reset to default
        # (by triggering the exception which causes a default reload)
        if profiles == {}:
            raise FileNotFoundError

        # attempt to load the previously used profile
        try:
            # the previous profile name is the text contents of restored_file
            with open(restored_filename) as restored_file:
                previous_profile_name = restored_file.read()

            # make the current profile the last used one
            # (if the last used one does not exist a KeyError will be raised)
            current = profiles[previous_profile_name]

        # if it was deleted then just load the first profile found in the dict
        except KeyError:
            logger.debug(f"Previous profile (\"previous_profile_name\") could not be located.")
            # obtain name of the first profile in the dict and set the current profile to it
            previous_profile_name = next(iter(profiles))
            logger.debug(f"Set \"{previous_profile_name}\" as the currently selected/loaded profile.")
            current = profiles[previous_profile_name]

    # if the settings file wasn't found then create a new one
    except FileNotFoundError:
        logger.debug("Settings file not found. Restoring defaults...")

        # default profile is for B-DNA
        current = profile(
            D=2.2,
            H=3.549,
            T=2,
            B=21,
            Z_c=0.17,
            Z_s=1.26,
            theta_b=34.29,
            theta_c=17.1428,
            theta_s=2.3,
        )

        # this will be the only profile in the master list
        # (since the master list of profiles is being created now)
        profiles = {"B-DNA": current}

        # set the previous_profile_name to B-DNA (the default)
        previous_profile_name = "B-DNA"

    # log that profiles were loaded
    logger.debug("Loaded profiles.")
    logger.debug(profiles)


def dump() -> None:
    """Dump persisting attributes of this module to a file"""
    with open(restored_filename, "w") as restored_file:
        restored_file.write(previous_profile_name)

    # dump settings to file in format current-profile, all-profiles
    with open(profiles_filename, "wb") as settings_file:
        pickle.dump(profiles, settings_file)
