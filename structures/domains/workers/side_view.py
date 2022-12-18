import itertools
import logging
import time
from collections import deque
from math import dist
from typing import List, Tuple, Literal

import numpy as np

import settings
from constants.directions import *
from structures.points import NEMid, Nucleoside
from structures.points.point import Point
from structures.strands import Strand, Strands
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

    def compute(self) -> Strands:
        """
        Compute Strands with all NEMids and Nucleosides.

        Returns:
            A Strands object with all the strands, computed based off of the domain's data.
        """
        # Store the time so that we can output the duration
        start_time = time.time()

        # Each domain (except the zeroth domain) is lined up such that the left side of the domain lines up exactly
        # with NEMids of the right side of the previous domain; however, each domain still has two helices.
        #
        # What we will do is compute the NEMids for the side of the domain that makes a connection with the
        # previous domain, and then we will compute the NEMids for the other side of the domain later.

        # Create an empty container for the strands of the up and down strand of each domain. The structure here is
        # a list of tuples, where each tuple is a pair of strands (one for the up strand and one for the down strand).
        # Each strand is a list of NEMid and Nucleoside objects.
        strands: List[Tuple[Strand, Strand]]
        strands = [(Strand(), Strand(),) for domain in self.domains.domains()]

        # Create containers for the z coords and angles that we are about to compute.
        all_zeroed_strand_z_coords: List[np.ndarray] = []
        all_zeroed_strand_x_coords: List[np.ndarray] = []
        all_zeroed_strand_angles: List[np.ndarray] = []

        # Create easy references to various nucleic acid settings. This is done to make the code more readable.
        theta_b = self.nucleic_acid_profile.theta_b
        Z_b = self.nucleic_acid_profile.Z_b
        B = self.nucleic_acid_profile.B

        # Each domain has a left_helix_count and a other_helix_count. The left_helix_count is a list with three
        # integers. The second integer in left_helix_count represents the number of NEMids to initially generate.
        for domain in self.domains.domains():
            # The "zeroed_strand" is the strand that makes connects to the previous domain. It is either UP or DOWN.
            # This strand is lined up so that it is able to touch the previous domain's right_helix_joint strand
            # (right_helix_joint is a direction of either UP or DOWN representing a helix of the previous domain).
            zeroed_strand_direction = domain.left_helix_joint
            other_strand_direction = inverse(zeroed_strand_direction)
            zeroed_strand_NEMid_count = domain.left_helix_count
            other_strand_NEMid_count = domain.other_helix_count

            if domain.index == 0:
                # The first domain is a special case. The z coord of the first NEMid of the first domain is 0.
                initial_z_coord = 0
                # as a result of having the initial z coord be set to zero, no shifts are needed.
                shifts = 0

            else:
                # The z coord of the first NEMid for other domains is the index of the greatest x coord of the previous
                # domain's strand. "np.argmax(arr)" returns the index of the greatest element in an array.
                initial_z_coord = all_zeroed_strand_z_coords[-1][np.argmax(all_zeroed_strand_x_coords[-1])]
                # Shift down the initial z coord. We can shift it down in increments of Z_b * B, which we will call the
                # "decrease_interval"
                decrease_interval = Z_b * B
                initial_z_coord -= np.ceil(initial_z_coord/decrease_interval) * decrease_interval

                # Let "shifts" be the number of excess NEMids at the bottom of the data point arrays. We will start
                # generating everything at Z_b/theta_b * shifts, and end at what the normal end index would be + shifts.
                shifts = abs(int(np.floor_divide(initial_z_coord, Z_b)))

                # Boost the initial z coord based off of the shifts.
                initial_z_coord += shifts * Z_b

            # If we start at a z coord that is not zero the angle must also start at a different angle accordingly.
            initial_angle = shifts * theta_b

            # Compute the final Z coord and angle to generate. Note that numpy.arange() does not include the final
            # value, so we add 1 to the final value. Also note that we boost based off of count[1]--the number of
            # additional NEMids the user wishes to generate at the top of the strand.
            final_angle = initial_angle + ((zeroed_strand_NEMid_count[1] + 1) * theta_b)
            final_z_coord = initial_z_coord + ((zeroed_strand_NEMid_count[1] + 1) * Z_b)

            # Generate all the angles. We begin at x=0 and step by theta_b/2 for domain.left_helix_count[1] times.
            # Note that we are generating the data for NEMids and Nucleosides, which is why we step by half a theta_b.
            zeroed_strand_angles = np.arange(
                initial_angle,  # when to start generating angles
                final_angle,  # when to stop generating angles
                theta_b/2  # the amount to step by for each angle
            )
            all_zeroed_strand_angles.append(zeroed_strand_angles)

            # Generate all the x coords. X coords are generated based off of the angles, so we will use map
            # Point.x_coord_from_angle onto a copy of current_angles.
            zeroed_strand_x_coords = np.array(
                [Point.x_coord_from_angle(angle, domain) for angle in zeroed_strand_angles]
            )
            all_zeroed_strand_x_coords.append(zeroed_strand_x_coords)

            # Generate all the z coords. We begin at z=0 and step by Z_b/2 for domain.left_helix_count[1] times. Note
            # that we are generating the data for NEMids and Nucleosides, which is why we step by half a Z_b.
            zeroed_strand_z_coords = np.arange(
                initial_z_coord,  # when to start generating z coords
                final_z_coord,  # when to stop generating z coords
                Z_b/2,  # the amount to step by for each z coord
            )
            all_zeroed_strand_z_coords.append(zeroed_strand_z_coords)

            # Now, using various attributes of the nucleic acid profile, we can easily compute the other_strand (the
            # strand that does not make a connection with the previous domain).
            other_strand_angles = zeroed_strand_angles + self.nucleic_acid_profile.g
            other_strand_x_coords = np.array(
                [Point.x_coord_from_angle(angle, domain) for angle in other_strand_angles]
            )
            other_strand_z_coords = zeroed_strand_z_coords + self.nucleic_acid_profile.Z_mate

            zeroed_strand_data = zip(zeroed_strand_x_coords, zeroed_strand_z_coords, zeroed_strand_angles)
            other_strand_data = zip(other_strand_x_coords, other_strand_z_coords, other_strand_angles)

            # Build the list of NEMid and Nucleosides objects to append to the strands container for the zeroed strand.
            for counter, (x_coord, z_coord, angle) in enumerate(zeroed_strand_data):
                if counter % 2:
                    # If the counter is odd, we are generating a NEMid.
                    zeroed_strand_NEMid = NEMid(x_coord=x_coord, z_coord=z_coord, angle=angle)
                    strands[domain.index][zeroed_strand_direction].append(zeroed_strand_NEMid)
                else:
                    # If the counter is even, we are generating a Nucleoside.
                    zeroed_strand_nucleoside = Nucleoside(x_coord=x_coord, z_coord=z_coord, angle=angle)
                    strands[domain.index][zeroed_strand_direction].append(zeroed_strand_nucleoside)
            # Build the list of NEMid and Nucleosides objects to append to the strands container for the other strand.
            for counter, (x_coord, z_coord, angle) in enumerate(other_strand_data):
                if counter % 2:
                    # If the counter is odd, we are generating a NEMid.
                    other_strand_NEMid = NEMid(x_coord=x_coord, z_coord=z_coord, angle=angle)
                    strands[domain.index][other_strand_direction].append(other_strand_NEMid)
                else:
                    # If the counter is even, we are generating a Nucleoside.
                    other_strand_nucleoside = Nucleoside(x_coord=x_coord, z_coord=z_coord, angle=angle)
                    strands[domain.index][other_strand_direction].append(other_strand_nucleoside)

            # Now that we have computed all of the base NEMids we can compute the extra lower and uppper NEMids.
            # The additional NEMids to place on top for each strand are count[2] and the additional NEMids to place
            # on the bottom are count[0]. Recall that count[1] is the number of NEMids to generate initially.
            strands[domain.index][zeroed_strand_direction].generate_NEMids(
                zeroed_strand_NEMid_count[0], domain, direction=DOWN,
            )
            strands[domain.index][zeroed_strand_direction].generate_NEMids(
                zeroed_strand_NEMid_count[2], domain, direction=UP,
            )

            for direction, helix in enumerate(strands[domain.index]):
                for point in helix.items:
                    point.domain = domain
                    point.direction = direction

        # Now that everything has been generated, we can assemble it into one large Strands object.
        listed_strands = []
        for up_strand, down_strand in strands:
            listed_strands.append(up_strand)
            listed_strands.append(down_strand)

        # Recolor the strands
        for index, strand in enumerate(listed_strands):
            strand.color = settings.colors["sequencing"]["greys"][index % 2]

        # Log the amount of time it took to generate the strands.
        logger.info(
            "Computed all Nucleosides and NEMids for the strands in %s seconds.",
            round((time.time() - start_time), 4)
        )

        return Strands(self.nucleic_acid_profile, listed_strands)

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
