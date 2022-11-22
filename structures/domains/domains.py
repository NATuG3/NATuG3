import logging
from copy import copy
from typing import List, Iterable

from helpers import inverse
from structures.domains import Domain

logger = logging.getLogger(__name__)


class Domains:
    """
    Container for multiple domains.

    Attributes:
        subunit: The domains within a single subunit.
        symmetry: The symmetry type. Also known as "R".
    """

    def __init__(self, domains: Iterable, symmetry: int):
        assert isinstance(domains, Iterable)
        assert isinstance(symmetry, int)
        self.subunit = Subunit(list(domains))
        self.symmetry = symmetry

    @property
    def domains(self):
        """
        Obtain a list of all the domains.

        Notes:
            - This returns a copy of each domain.
            - The output is based off of self.subunit.domains.
        """
        output = []
        for cycle in range(self.symmetry):
            for domain in self.subunit.domains:
                output.append(copy(domain))
        for index, domain in enumerate(output):
            domain.index = index
        return output

    @property
    def count(self):
        """Total number of domains"""
        return self.subunit.count * self.symmetry


class Subunit:
    def __init__(self, domains: List[Domain]) -> None:
        assert isinstance(domains, list)
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
            i = 0
            while self.count < new:
                previous_domain = self.domains[-1]
                # the new template domains will be of altering strand directions with assumed
                # strand switches of 0
                self.domains.append(
                    Domain(
                        i,
                        previous_domain.theta_interior_multiple,
                        [inverse(previous_domain.helix_joints[1])] * 2,
                        previous_domain.count,
                    )
                )
                i += 1
