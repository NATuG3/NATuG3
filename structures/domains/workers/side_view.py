import itertools
import logging
from collections import deque
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

        # Create an empty container for the strands of the up and down strand of each domain. The structure here is
        # a list of tuples, where each tuple is a pair of strands (one for the up strand and one for the down strand).
        # Each strand is a list of NEMid and Nucleoside objects.
        strands: List[Tuple[List[NEMid | Nucleoside], List[NEMid | Nucleoside]]]
        strands = [([], [],) for domain in self.domains.domains()]

        # Create containers for the z coords and angles that we are about to compute.
        z_coords: List[np.ndarray] = []
        x_coords: List[np.ndarray] = []
        angles: List[np.ndarray] = []

        # Each domain has a left_helix_count and a other_helix_count. The left_helix_count is a list with three
        # integers. The second integer in left_helix_count represents the number of NEMids to initially generate.
        for domain in self.domains.domains():
            # The "zeroed_strand" is the strand that makes connects to the previous domain. It is either UP or DOWN.
            # This strand is lined up so that it is able to touch the previous domain's right_helix_joint strand
            # (right_helix_joint is a direction of either UP or DOWN representing a helix of the previous domain).
            zeroed_strand = domain.left_helix_joint
            count = domain.left_helix_count[1]
            if domain.index == 0:
                # The first domain is a special case. The z coord of the first NEMid of the first domain is 0.
                initial_z_coord = 0
            else:
                # The z coord of the first NEMid for other domains is the index of the greatest x coord of the previous
                # domain's strand. "np.argmax(arr)" returns the index of the greatest element in an array.
                initial_z_coord = z_coords[-1][np.argmax(x_coords[-1])]

            # Generate all the angles. We begin at x=0 and step by theta_b for domain.left_helix_count[1] times.
            current_angles = np.arange(
                0,
                count,
                self.nucleic_acid_profile.theta_b
            )
            angles.append(current_angles)

            # Generate all the x coords. X coords are generated based off of the angles, so we will use map
            # Point.x_coord_from_angle onto a copy of current_angles.
            current_x_coords = np.array([Point.x_coord_from_angle(angle, domain) for angle in current_angles])
            x_coords.append(current_x_coords)

            # Generate all the z coords. We begin at z=0 and step by Z_b for domain.left_helix_count[1] times.
            current_z_coords = np.arange(
                initial_z_coord,
                count,
                self.nucleic_acid_profile.Z_b,
            )
            z_coords.append(current_z_coords)

            # Build the list of NEMid and Nucleosides objects to append to the strands container.
            for x_coord, z_coord, angle in zip(current_x_coords, current_z_coords, current_angles):
                # Create a NEMid object and append it to the strands container.
                NEMid_ = NEMid(
                    x_coord=x_coord,
                    z_coord=z_coord,
                    angle=angle,
                    direction=zeroed_strand,
                    domain=domain,
                )
                strands[domain.index][zeroed_strand].append(NEMid_)

                # Recompute the x coord and z coord for the nucleoside that comes after the NEMid.
                z_coord += self.nucleic_acid_profile.Z_b
                angle += self.nucleic_acid_profile.theta_b
                x_coord = Point.x_coord_from_angle(angle, domain)

                # Create a Nucleoside object and append it to the strands container.
                nucleoside = Nucleoside(
                    x_coord=x_coord,
                    z_coord=z_coord,
                    angle=angle,
                    direction=zeroed_strand,
                    domain=domain,
                )
                strands[domain.index][zeroed_strand].append(nucleoside)

        print(strands)
        return strands

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
