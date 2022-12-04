from copy import deepcopy
from typing import List

from structures.domains import Domain


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
        self.domains = domains

    def __deepcopy__(self):
        """Create a deep copy of a subunit object."""
        new_domains = deepcopy(self.domains)
        return Subunit(new_domains)

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
                        [inverse(previous_domain.helix_joints[1])] * 2,
                        previous_domain.count,
                    )
                )
                i += 1
