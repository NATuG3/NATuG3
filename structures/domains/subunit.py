from copy import copy
from typing import Iterable, List

from helpers import inverse
from structures.profiles import NucleicAcidProfile


class Subunit:
    """
    A domain subunit. Contains all the domains for a given subunit.

    The parent of a Subunit is a Domains object. There is thorough integration with the parenting
    of subunits, domains, domain.

    Notes:
        - If this is a template subunit then it is frozen and immutable.
        - If the subunit.count is increased/decreased then subunit.domains changes too.

    Attributes:
        nucleic_acid_profile: The nucleic acid configuration.
        domains: The domains in the subunit.
        count: The number of domains in the subunit.
        template: Whether this is a template subunit.
        parent: The parent Domains object.

    Methods:
        append()
        remove()
    """

    def __init__(
        self,
        nucleic_acid_profile: NucleicAcidProfile,
        domains: List["Domain"],
        template: bool = False,
        parent: "Domains" = None,
    ) -> None:
        """
        Create an instance of a subunit container.

        Args:
            nucleic_acid_profile: The nucleic acid configuration.
            domains: The domains in the subunit.
            template: Whether this subunit is a template subunit. Defaults to False.
                If this is not a template subunit then the subunit becomes immutable.
                In other words, only template subunits can be modified.
            parent: The parent Domains object.
        """
        self.template = template  # must be the first property set
        self.parent = parent
        self.nucleic_acid_profile = nucleic_acid_profile
        self.domains = domains

        # assign the parent of all the domains to us
        for domain in self.domains:
            domain.parent = self

        assert isinstance(domains, Iterable)

    def append(self, domain: "Domain") -> None:
        """
        Append a worker to the subunit and parent it.

        Args:
            domain: The domain to append to the subunit.

        Notes:
            The domain will have its parent set to this subunit.
        """
        self.domains.append(domain)
        domain.parent = self

    def remove(self, domain: "Domain") -> None:
        """
        Remove a worker from the subunit.

        Args:
            domain: The domain to remove from the subunit.

        Notes:
            The domain will have its parent reset to None.
        """
        self.domains.remove(domain)
        domain.parent = None

    def __setattr__(self, key, value):
        """
        Prevent users from mutating a non-template subunit.

        If the template property is changed then modify whether the domains are stored
        in a list or tuple based on whether this is a template subunit or not. I.E. if this is not a template
        subunit, the array of domains will become immutable.

        Args:
            key: The attribute to set.
            value: The value to set the attribute to.

        Raises:
            ValueError: If the subunit is not a template subunit and the user is trying to mutate it.
        """
        if key == "template":
            try:
                # force self.domains to be a tuple or list based off of whether this is a template
                # subunit or not. Non template subunits should be fully immutable.
                if value:  # if this is a template subunit
                    super().__setattr__("domains", tuple(self.domains))
                else:  # if this is no longer a template subunit
                    super().__setattr__("domains", list(self.domains))
            except AttributeError:
                super().__setattr__(key, value)
        else:
            if self.template:
                # if this is the template subunit then set the attr as normal
                # but then also reset the parent's cache if the parent of this instance isn't None
                if key != "parent" and self.parent is not None:
                    self.parent.clear_cache()
                # then set the attr as normal
                super().__setattr__(key, value)
            else:  # but if it isn't a template subunit then raise an error
                raise ValueError("Nontemplate Subunits cannot be modified.")

    def copy(self) -> "Subunit":
        """
        Obtain a copy of a subunit object.

        Returns:
            A brand-new subunit object with brand-new domain objects (which are identical copies).
        """
        return Subunit(
            self.nucleic_acid_profile,
            [copy(domain) for domain in self.domains],
            template=self.template,
            parent=self.parent,
        )

    @property
    def count(self) -> int:
        """
        Obtain the number of domains in the subunit.

        Returns:
            The number of domains in the subunit.
        """
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
        # we couldn't import domains before because it was partially initialized
        # but we can now (and we will need it if the count increases to make new domains)
        from structures.domains import Domain

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
                        self.nucleic_acid_profile,
                        previous_domain.theta_interior_multiple,
                        inverse(previous_domain.right_helix_joint),
                        inverse(previous_domain.right_helix_joint),
                        previous_domain.count,
                        parent=self
                    )
                )
                i += 1

    def __repr__(self) -> str:
        """
        Obtain a string representation of the subunit.

        Returns:
            A string representation of the subunit.
        """
        return f"Subunit({self.domains})"
