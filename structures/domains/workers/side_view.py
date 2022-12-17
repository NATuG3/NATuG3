import itertools
import logging
from math import dist
from typing import List, Tuple, Literal

import numpy as np

import settings
from constants.directions import *
from structures.points import NEMid, Nucleoside
from structures.points.point import Point
from structures.strands import Strand
from utils import inverse

logger = logging.getLogger(__name__)


class DomainStrandWorker:
    """
    Class for generating data needed for a side view graph of helices.
    This is used by the Domains structure to compute strands for its child workers.

    Attributes:
        domains: The domains to compute strands for.
        nucleic_acid_profile: The nucleic acid nucleic_acid_profile to use for computing strands.

    Methods:
        compute()
    """

    strand_directions = (UP, DOWN)
    cache_clearers = ("workers", "profiles")

    def __init__(self, domains: "Domains") -> None:
        """
        Initialize a side view generator object.

        Args:
            domains: The workers to compute sequencing for.
        """
        self.nucleic_acid_profile = domains.nucleic_acid_profile
        self.domains = domains

    def compute(
        self,
    ) -> List[Tuple[List[NEMid | Nucleoside], List[NEMid | Nucleoside]]]:
        """
        Compute all NEMid data.

        Returns:
            Strands object for all sequencing that the workers can create.
        """
        # Each domain (except the zeroth domain) is lined up such that the left side of the domain lines up exactly
        # with NEMids of the right side of the previous domain; however, each domain still has two helices.
        #
        # What we will do is compute the NEMids for the side of the domain that makes a connection with the
        # previous domain, and then we will compute the NEMids for the other side of the domain later.

        # Since Strand objects are able to self generate NEMids, first we create the needed strands.
        strands = []
        for domain in self.domains:
            # Create and store an up and down strand for each domain
            strands.append([Strand(), Strand()])
            # Give the up and down strand distinct colors
            strands[-1][0].color = settings.colors["sequencing"]["greys"][0]
            strands[-1][1].color = settings.colors["sequencing"]["greys"][0]

        # Each domain has a left_helix_count and a right_helix_count

    def __repr__(self) -> str:
        """
        Return a string representation of the side view worker.

        Includes:
            - the domains
            - the nucleic acid nucleic_acid_profile

        Returns:
            str: A string representation of the side view worker.
        """
        return f"SideViewWorker(domains={self.domains}, nucleic_acid_profile={self.nucleic_acid_profile})"

    def __len__(self):
        return self.domains.domains.count
