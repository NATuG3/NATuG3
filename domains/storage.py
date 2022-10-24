import atexit
import logging
import os
import pickle

import settings
from constants.directions import *
from domains.datatypes import Domains, Domain

restored_filename = f"domains/restored.{settings.extension}"

current = None
settings = None

logger = logging.getLogger(__name__)


def load():
    """Load the previous state of domains."""
    global current

    atexit.register(dump)

    if restored_filename in os.listdir():
        with open(restored_filename, "rb") as restored_file:
            current = pickle.load(restored_file)
        logger.info("Restored previous domain editor state.")
    else:
        logger.warning(
            "Previous domain editor state save file not found. Loading defaults..."
        )
        current = default


def dump():
    """Save current domains state for state restoration on load."""
    with open(restored_filename, "wb") as restored_file:
        # perform data validation before save
        if not isinstance(current, Domains):
            logger.critical("Data validation for domains dump failed.")
            raise TypeError("Domains container is of wrong type.", current)
        pickle.dump(current, restored_file)


default = Domains(([Domain(9, (UP, UP), 50)] * 14), 1)
