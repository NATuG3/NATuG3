import atexit
import logging
import pickle

import refs
import settings
from constants.directions import *
from structures.domains import Domains, Domain

logger = logging.getLogger(__name__)


class _Domains:
    filename: str = f"saves/domains/restored.{settings.extension}"
    default: Domains = Domains(
        refs.nucleic_acid.current,
        (
            Domain(refs.nucleic_acid.current, 9, UP, UP, 50),
            Domain(refs.nucleic_acid.current, 9, DOWN, DOWN, 50),
            Domain(refs.nucleic_acid.current, 9, UP, UP, 50),
            Domain(refs.nucleic_acid.current, 9, DOWN, DOWN, 50),
            Domain(refs.nucleic_acid.current, 9, UP, UP, 50),
            Domain(refs.nucleic_acid.current, 9, DOWN, DOWN, 50),
            Domain(refs.nucleic_acid.current, 9, UP, UP, 50),
        ),
        2,
        True,
    )

    def __init__(self):
        self.load()
        self.current = self.default
        atexit.register(self.dump)

    def load(self):
        try:
            with open(self.filename, "rb") as filename:
                self.current = pickle.load(filename)
            logger.info("Restored previous domain editor state.")
        except FileNotFoundError:
            logger.warning(
                "Previous domain editor state save file not found. Defaults restored."
            )

    def dump(self):
        """Save current domains state for state restoration on load."""
        with open(self.filename, "wb") as restored_file:
            # perform data validation before save
            if not isinstance(self.current, Domains):
                logger.critical("Data validation for domains dump failed.")
                raise TypeError("Domains container is of wrong type.", self.current)
            pickle.dump(self.current, restored_file)
