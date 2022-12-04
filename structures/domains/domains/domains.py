import logging
from copy import deepcopy
from functools import cache
from typing import List, Iterable, Type

import settings
from constants.directions import DOWN, UP
from helpers import inverse
from structures.domains.domains.worker import DomainStrandWorker
from structures.domains.subunit import Subunit
from structures.profiles import NucleicAcidProfile
from structures.strands import Strand, Strands

logger = logging.getLogger(__name__)


class Domains:
    """
    Container for multiple domains.

    Attributes:
        nucleic_acid_profile: The nucleic acid configuration.
        subunit: The domains within a single subunit.
            This is a template subunit. Note that subunits can be mutated.
        subunits: All subunits. Only the first one can be written to.
        symmetry: The symmetry type. Also known as "R".
        strands: All the strands of all the domains.
        count: The total number of domains. Includes domains from all subunits.
        antiparallel: Whether the domains are forced to have alternating upness/downness.

    Methods:
        strands()
        top_view()
        domains()
        subunits()
    """

    def __init__(
        self,
        nucleic_acid_profile: NucleicAcidProfile,
        domains: Iterable["Domain"],
        symmetry: int,
        antiparallel: bool = False,
    ) -> None:
        """
        Initialize a Domains object.

        Args:
            nucleic_acid_profile: The nucleic acid configuration.
            domains: All the domains for the template subunit.
            symmetry: The symmetry type. Also known as "R".
            antiparallel: Whether the domains are forced to have alternating upness/downness.
        """
        # store various settings
        self.nucleic_acid_profile = nucleic_acid_profile
        self.symmetry = symmetry
        self.antiparallel = antiparallel

        # self.subunit is the template subunit
        # meaning that all other subunits are based off of this one
        self.subunit = Subunit(domains, template=True)

        # create a worker object for computing strands for domains
        self.worker = DomainStrandWorker(self.nucleic_acid_profile, self.domains)

    @property
    def count(self) -> int:
        """
        The number of domains in the Domains object.

        Returns:
            The number of domains in the Domains object.
        """
        return len(self.domains())

    def subunits(self) -> List[Subunit]:
        """
        Obtain all subunits of the Domains object.

        Returns:
            List[Subunit]: Copies of the template subunit for all subunits except the first one.
            The first subunit in the returned list is a direct reference to the template subunit.
        """
        subunits = []
        for cycle in range(self.symmetry):
            # for all subunits after the first one make deep copies of the subunit.
            if cycle == 0:
                subunits.append(self.subunit)
            else:
                subunits.append(self.subunit.copy())
        return subunits

    def domains(self) -> List["Domain"]:
        """
        Obtain a list of all domains from all subunits.

        Returns:
            A list of all domains from all subunits.
        """
        domains = []
        for subunit in self.subunits():
            domains.extend(subunit.domains)

        # if the domains instance is set to antiparallel then make the directions
        # of the domains alternate.
        if self.antiparallel:
            direction = self.subunit.domains[-1].right_helix_joint
            for domain in domains:
                domain.left_helix_joint = direction
                domain.right_helix_joint = direction
                direction = inverse(direction)

        # apply ourself as the parent for each domain
        for domain in domains:
            domain.parent = self

        return domains

    @cache
    def strands(self) -> Strands:
        """
        Obtain a list of all strands from all domains.

        Notes:
            - The strands returned are references to the strands in the domains. This means
                that if the outputted strands are modified then the domains' strands will be modified too.

        Returns:
            A list of all strands from all domains.
        """
        strands = DomainStrandWorker(self.nucleic_acid_profile, self.domains)

        converted_strands = []
        for strand_direction in (
            UP,
            DOWN,
        ):
            for index, domain in enumerate(strands.domains.domains()):
                converted_strands.append(
                    Strand(
                        self.nucleic_acid_profile,
                        strands[index][strand_direction],
                        color=settings.colors["sequencing"]["greys"][strand_direction],
                    )
                )

        # convert sequencing from a list to a Strands container
        return Strands(self.nucleic_acid_profile, converted_strands)

    def __repr__(self) -> str:
        """
        Obtain a string representation of the Domains object.

        Returns:
            A string representation of the Domains object.
        """
        return (
            f"Domains("
            f"template_subunit={self.subunit},"
            f"domain_count={self.count},"
            f"antiparallel={self.antiparallel},"
            f"symmetry={self.symmetry}"
            f")"
        )
