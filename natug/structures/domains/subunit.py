from copy import copy
from typing import Iterable, List

from natug.structures.profiles import NucleicAcidProfile
from natug.utils import inverse


class Subunit:
    """
    A domain subunit. Contains all the domains for a given subunit.

    The strands of a Subunit is a Domains object. There is thorough integration with the
    parenting of subunits, domains, domain.

    Notes:
        - If this is a template subunit then it is frozen and immutable.
        - If the subunit.count is increased/decreased then subunit.domains changes too.

    Attributes:
        nucleic_acid_profile: The nucleic acid configuration.
        domains: The domains in the subunit.
        count: The number of domains in the subunit.
        template: Whether this is a template subunit.
        parent: The strands Domains object.

    Methods:
        append()
        remove()
        inverted()
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
            parent: The strands Domains object.
        """
        self.template = template  # must be the first property set
        self.domains = domains
        self.parent = parent
        self.nucleic_acid_profile = nucleic_acid_profile

        # assign the strands of all the domains to us
        for domain in self.domains:
            domain.parent = self

        assert isinstance(domains, Iterable)

    def append(self, domain: "Domain") -> None:
        """
        Append a worker to the subunit and strands it.

        Args:
            domain: The domain to append to the subunit.

        Notes:
            The domain will have its strands set to this subunit.
        """
        self.domains.append(domain)
        domain.parent = self

    def remove(self, domain: "Domain") -> None:
        """
        Remove a worker from the subunit.

        Args:
            domain: The domain to remove from the subunit.

        Notes:
            The domain will have its strands reset to None.
        """
        self.domains.remove(domain)
        domain.parent = None

    def copy(self) -> "Subunit":
        """
        Obtain a copy of a subunit object.

        Returns:
            A brand-new subunit object with brand-new domain objects
            (which are identical copies).
        """
        return Subunit(
            self.nucleic_acid_profile,
            [copy(domain) for domain in self.domains],
            template=self.template,
            parent=self.parent,
        )

    def inverted(self) -> "Subunit":
        """
        Obtain an inverted copy of the subunit.

        An inverted subunit is a subunit with all of its domains helix joint directions
        inverted.

        Returns:
            A brand-new subunit object with brand-new domain objects.
        """
        return Subunit(
            self.nucleic_acid_profile,
            [domain.inverted() for domain in self.domains],
            False,
            self.domains,
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

        * When the count is increased new domains are added with alternating helix
            joints but with the same settings. Looks at the right helix joint of the last
            domain to begin the oscillation of parallel-ness.
        * When the count is decreased domains are trimmed off of the end of the subunit.

        Args:
            new: The new count for the subunit.
                The number of domains changes based off the difference between this
                and the previous count.
        """
        # we couldn't import domains before because it was partially initialized but
        # we can now (and we will need it if the count increases to make new domains)
        from natug.structures.domains import Domain

        # if the subunit count has decreased then trim off extra domains
        if new < self.count:
            self.domains = self.domains[:new]
        # if the subunit count has increased then add placeholder domains based on
        # last domain in domain list
        else:
            i = 0
            while self.count < new:
                previous_domain = self.domains[-1]
                # the new template domains will be of altering strand directions with
                # assumed strand switches of 0
                self.domains.append(
                    Domain(
                        self.nucleic_acid_profile,
                        theta_m_multiple=previous_domain.theta_m_multiple,
                        left_helix_joint=inverse(previous_domain.right_helix_joint),
                        right_helix_joint=inverse(previous_domain.right_helix_joint),
                        up_helix_count=previous_domain.up_helix_count,
                        down_helix_count=previous_domain.down_helix_count,
                        parent=self,
                    )
                )
                i += 1

    def __getitem__(self, item):
        """
        Obtain a domain from the subunit.

        Args:
            item: The index of the domain to obtain.

        Returns:
            The domain at the given index.
        """
        return self.domains[item]

    def __repr__(self) -> str:
        """
        Obtain a string representation of the subunit.

        Returns:
            A string representation of the subunit.
        """
        return f"Subunit({self.domains})"
