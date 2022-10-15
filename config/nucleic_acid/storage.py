from dataclasses import dataclass
import logging
import pickle
import atexit
import config.settings

profiles_filename = f"config/nucleic_acid/profiles.{config.settings.extension}"
restored_filename = f"config/nucleic_acid/restored.{config.settings.extension}"

count: int = 50  # initial NEMids/strand count
current: object = None  # current profile
profiles: dict = None  # all profiles

# set up logger
logger = logging.getLogger(__name__)


@dataclass
class Profile:
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

    def __eq__(self, other: object) -> bool:
        """Returns true if identical profile is returned"""
        if isinstance(other, Profile):
            return vars(self) == vars(other)
        else:
            return False


def load() -> None:
    global current
    global profiles

    # ensure settings save on program exit
    atexit.register(dump)

    # attempt to load the nucleic acid settings file
    try:
        # load all profiles
        with open(profiles_filename, "rb") as settings_file:
            profiles = pickle.load(settings_file)
            assert isinstance(profiles, dict)

        # load restored settings
        with open(restored_filename, "rb") as restored_file:
            current = pickle.load(restored_file)
            assert isinstance(current, Profile)

        logger.debug("Saved profiles file loaded.")
    # if the settings file wasn't found then create a new one
    except FileNotFoundError:
        logger.warning("Saved profiles file not found. Restoring defaults...")
        profiles = defaults
        current = next(iter(defaults.values()))

    # log that profiles were loaded
    logger.debug("Loaded profiles.")
    logger.debug(profiles)


def dump() -> None:
    """Dump persisting attributes of this module to a file"""
    # dump all profiles
    with open(profiles_filename, "wb") as settings_file:
        assert isinstance(profiles, dict)

        # perform data validation before save
        for name, profile in profiles.items():
            if not isinstance(profile, Profile):
                logger.critical(
                    "Data validation for nucleic_acid profiles dump failed."
                )
                raise TypeError(f'profile named "{name}" is not a profile', profile)

        pickle.dump(profiles, settings_file)
        logger.info(f'Dumped all profiles into "{settings_file}"')

    # dump current settings
    with open(restored_filename, "wb") as settings_file:

        # perform data validation before save
        if not isinstance(current, Profile):
            logger.critical(
                "Data validation for nucleic_acid current profile dump failed."
            )
            raise TypeError("current is not a profile", profile)

        pickle.dump(current, settings_file)
        logger.info(f'Dumped current nucleic_acid settings into "{settings_file}"')


# defaults
defaults = {
    "B-DNA (MFD)": Profile(
        D=2.2,
        H=3.549,
        T=2,
        B=21,
        Z_c=0.17,
        Z_s=1.26,
        theta_b=34.29,
        theta_c=17.1428,
        theta_s=2.343,
    )
}
