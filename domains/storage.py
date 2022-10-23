import atexit
import logging
import pickle
from typing import List

import config.settings
from computers.datatypes import Domain
from constants.directions import *
from helpers import inverse

restored_filename = f"domains/restored.{config.extension}"

current = None
settings = None

logger = logging.getLogger(__name__)


class Subunit:
    def __init__(self, domains: List[Domain]) -> None:
        self.domains = domains

    @property
    def count(self) -> int:
        """Number of domains per subunit."""
        return len(self.domains)

    @count.setter
    def count(self, new):
        # if the subunit count has decreased then trim off extra domains
        if new < self.count:
            self.domains = self.domains[:new]
        # if the subunit count has increased then add placeholder domains based on last domain in domain list
        else:
            while self.count < new:
                previous_domain = self.domains[-1]
                # the new template domains will be of altering strand directions with assumed
                # strand switches of 0
                self.domains.append(
                    Domain(
                        previous_domain.theta_interior_multiple,
                        [inverse(previous_domain.helix_joints[1])] * 2,
                        previous_domain.count,
                    )
                )


class Domains:
    """
    Container for multiple domains.
    """

    def __init__(self, domains, symmetry):
        self.subunit = Subunit(domains)
        self.symmetry = symmetry

    @property
    def domains(self):
        """List of all domains."""
        return tuple(self.subunit.domains * self.symmetry)

    @property
    def count(self):
        """Total number of domains"""
        return self.subunit.count * self.symmetry


def load():
    """Load the previous state of domains."""
    global current

    atexit.register(dump)

    try:
        with open(restored_filename, "rb") as restored_file:
            current = pickle.load(restored_file)
        logger.info("Restored previous domain editor state.")
    except FileNotFoundError:
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
