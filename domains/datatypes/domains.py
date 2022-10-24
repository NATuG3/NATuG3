from typing import List

from domains.datatypes import Domain
from helpers import inverse


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
