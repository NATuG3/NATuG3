import pickle
import logging
from config import properties
import datatypes


filename = "settings.nano"
logger = logging.getLogger(__name__)


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
        pickle.dump((properties.current, properties.profiles), settings_file)


def load():
    """Load persisting attributes of this module from a file"""

    try:
        logger.debug("Settings file found. Loading setting profiles...")
        # attempt to open the settings file, or create a new settings file with
        # DNA-B settings (as a default/example)
        with open(filename, "rb") as settings_file:
            properties.current, properties.profiles = pickle.load(settings_file)
    except FileNotFoundError:
        logger.debug("Settings file not found. Restoring defaults...")
        properties.current = datatypes.profile(
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
        properties.profiles = {"B-DNA": properties.current}

    logger.debug("Loaded profiles.")
    logger.debug(properties.profiles)
