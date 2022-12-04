import logging
from copy import copy
from typing import List, Iterable

from constants.directions import *
from helpers import inverse
from structures.domains import Domain
from structures.domains.subunit import Subunit

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
        self, domains: Iterable, symmetry: int, antiparallel: bool
    ) -> None:
        """
        Initialize a Domains container.

        Args:
            domains: A list of domains of a single subunit.
            symmetry: The symmetry type. Also known as "R".
        """
        self.subunit = Subunit(list(domains))
        self.antiparallel = antiparallel
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
        if self.antiparallel:
            direction = UP
            for index, domain in enumerate(output):
                output[index].helix_joints = [direction, direction]
                direction = inverse(direction)

        return output

    @property
    def count(self) -> int:
        """Total number of domains."""
        return self.subunit.count * self.symmetry
