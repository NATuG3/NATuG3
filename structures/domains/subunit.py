from copy import deepcopy
from copy import deepcopy
from typing import Type, Iterable

from helpers import inverse


class Subunit:
    """
    A domain subunit. Contains all the domains for a given subunit.

    Notes:
        - If this is a template subunit then it is frozen and immutable.
        - If the subunit.count is increased/decreased then subunit.domains changes too.

    Attributes:
        domains: The domains in the subunit.
        count: The number of domains in the subunit.
        template: Whether this is a template subunit.
    """

    def __init__(
        self, domains: Iterable["Domain"], template: bool = False
    ) -> None:
        """
        Create an instance of a subunit container.

        Args:
            domains: The domains in the subunit.
            template: Whether this subunit is a template subunit. Defaults to False.
                If this is not a template subunit then the subunit becomes immutable.
                In other words, only template subunits can be modified.
        """
        self.template = template
        self.domains = domains

    def __setattr__(self, key, value):
        """
        Prevent users from mutating a non-template subunit.

        If the template property is changed then modify whether the domains are stored
        in a list or tuple based on whether this is a template subunit or not.
        """
        if key == "template":
            try:
                if value:  # if this is a template subunit
                    super().__setattr__("domains", tuple(self.domains))
                else:  # if this is no longer a template subunit
                    super().__setattr__("domains", list(self.domains))
            except AttributeError:
                super().__setattr__(key, value)
        else:
            if (
                self.template
            ):  # if this is the template subunit then set the attr as normal
                super().__setattr__(key, value)
            else:  # but if it isn't a template subunit then raise an error
                raise ValueError("Nontemplate Subunits cannot be modified.")

    def copy(self) -> "Subunit":
        """
        Obtain a copy of a subunit object.

        Returns:
            A brand new subunit object with brand new domain objects.
        """
        return Subunit(deepcopy(self.domains), self.template)

    @property
    def count(self) -> int:
        """Obtain the number of domains in the subunit."""
        return len(self.domains)

    @count.setter
    def count(self, new) -> None:
        """
        Change the number of domains in the subunit.

        * When the count is increased new domains are added with alternating helix joints but
        with the same settings. Looks at the right helix joint of the last domain to begin the
        oscillation of parallel-ness.
        * When the count is decreased domains are trimmed off of the end of the subunit.

        Args:
            new: The new count for the subunit.
                The number of domains changes based off the difference between this
                and the previous count.
        """
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
                        [inverse(previous_domain.right_helix_joint)] * 2,
                        previous_domain.count,
                    )
                )
                i += 1
