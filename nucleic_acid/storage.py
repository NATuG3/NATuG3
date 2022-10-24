import atexit
import logging
import os
import pickle

import settings
from .datatypes import Profile

profiles_filename = f"nucleic_acid/profiles.{settings.extension}"
restored_filename = f"nucleic_acid/restored.{settings.extension}"

count: int = 50  # initial NEMids/strand count
current: object = None  # current profile
profiles: dict = None  # all profiles

# set up logger
logger = logging.getLogger(__name__)


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
