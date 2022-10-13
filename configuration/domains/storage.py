import logging
import configuration.settings
from constants.directions import *
import pickle
import atexit
from dataclasses import dataclass
from computers.datatypes import Domain
from typing import List
from helpers import inverse


restored_filename = f"configuration/domains/restored.{configuration.settings.extension}"

current = None
settings = None

logger = logging.getLogger(__name__)


@dataclass()
class Domains:
    """
    Container for multiple domains.
    """
    subunit_domains: List[Domain]
    symmetry: int

    @property
    def domains(self):
        """List of all domains."""
        return tuple(self.subunit_domains * self.symmetry)

    @property
    def subunit_count(self):
        """Number of domains per subunit."""
        return len(self.subunit_domains)

    @subunit_count.setter
    def subunit_count(self, new_subunit_count):
        # if the subunit count has decreased then trim off extra domains
        if new_subunit_count < self.subunit_count:
            self.subunit_domains = self.subunit_domains[:new_subunit_count]
        # if the subunit count has increased then add placeholder domains based on last domain in domain list
        else:
            while self.subunit_count < new_subunit_count:
                previous_domain = self.subunit_domains[-1]
                # the new template domains will be of altering strand directions with assumed
                # strand switches of 0
                self.subunit_domains.append(
                    Domain(
                        previous_domain.theta_interior_multiple,
                        [inverse(previous_domain.helix_joints[1])] * 2,
                        previous_domain.count
                           )
                )

    @property
    def total_count(self):
        """Total number of domains"""
        return self.subunit_count * self.symmetry


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
            raise TypeError(
                "Domains container is of wrong type.", Domains
            )
        pickle.dump(current, restored_file)


default = Domains(([Domain(9, (UP, UP), 50)] * 14), 1)
