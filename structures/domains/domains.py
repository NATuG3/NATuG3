import logging
from copy import copy
from typing import List, Iterable

from constants.directions import *
from helpers import inverse
from structures.domains import Domain

logger = logging.getLogger(__name__)


class Domains:
    """
    Container for multiple domains.

    Attributes:
        subunit: The domains within a single subunit.
        domains: All domains of all subunits.
        count: The total number of domains. Includes domains from all subunits.
        symmetry: The symmetry type. Also known as "R".
    """

    def __init__(
        self, domains: Iterable, symmetry: int, auto_antiparallel: bool
    ) -> None:
        """
        Initialize a domains container.

        Args:
            domains: A list of domains of a single subunit.
            symmetry: The symmetry type. Also known as "R".
        """
        self.subunit = Subunit(list(domains))
        self.auto_antiparallel = auto_antiparallel
        self.symmetry = symmetry

    @property
    def domains(self) -> list[Domain]:
        """
        List of all the domains.

        Notes:
            - This returns a copy of each domain.
            - The output is based off of self.subunit.domains.
        """
        # compute an output that is symmetry number of copies of a subunit
        output: List[Domain] = []
        for cycle in range(self.symmetry):
            for domain in self.subunit.domains:
                output.append(copy(domain))
        for index, domain in enumerate(output):
            domain.index = index

        # force antiparallelity if self.autoparallel
        if self.auto_antiparallel:
            direction = UP
            for index, domain in enumerate(output):
                output[index].helix_joints = [direction, direction]
                direction = inverse(direction)

        return output

    @property
    def count(self) -> int:
        """Total number of domains."""
        return self.subunit.count * self.symmetry


class Subunit:
    """
    A domain subunit.

    Attributes:
        domains: The domains in the subunit.
        count: The number of domains in the subunit.
    """

    def __init__(self, domains: List[Domain]) -> None:
        """
        Create an instance of a subunit container.

        Args:
            domains: The domains in the subunit.
        """
        assert isinstance(domains, list)
        self.domains = domains

    @property
    def count(self) -> int:
        """Number of domains in the subunit."""
        return len(self.domains)

    @count.setter
    def count(self, new):
        """Change the number of domains in the subunit."""
        # if the subunit count has decreased then trim off extra domains
        if new < self.count:
            self.domains = self.domains[:new]
        # if the subunit count has increased then add placeholder domains based on last domain in domain list
        else:
            i = 0
            while self.count < new:
                previous_domain = self.domains[-1]
                # the new template domains will be of altering strand directions with assumed
                # strand switches of 0
                self.domains.append(
                    Domain(
                        i,
                        previous_domain.theta_interior_multiple,
                        [inverse(previous_domain.right_helix_joint_direction)] * 2,
                        previous_domain.count,
                    )
                )
                i += 1
