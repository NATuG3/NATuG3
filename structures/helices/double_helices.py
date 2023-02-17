from math import ceil
from typing import List

import numpy as np
from numpy import argmax

from constants.directions import DOWN, UP
from structures.domains import Domains
from structures.helices import DoubleHelix
from structures.helices.helix import Helix
from utils import inverse


class DoubleHelices:
    """
    A container for multiple double helices.

    A Helix's parent is a DoubleHelix. A DoubleHelix's parent is a DoubleHelices.

    This class is able to compute point data for each helix, based on its relation to
    the adjacent helices.

    Attributes:
        double_helices: A list of DoubleHelix objects.
        nucleic_acid_profile: The nucleic acid profile to use for computations.

    Methods:
        domains: Obtain all the domains of all the double helices in their respective
            order.
        compute: Compute the point data for each helix. The data will be stored in the
            helices respective x coord, z coord, and angle arrays.
    """

    __slots__ = "double_helices", "nucleic_acid_profile"

    def __init__(self, domains: Domains, nucleic_acid_profile) -> None:
        """
        Initialize a container for DoubleHelix objects.

        The size to make the data arrays of each helix is determined based on the
        domains' GenerationCounts.

        Args:
            domains: A list of Domain objects.
            nucleic_acid_profile: The nucleic acid profile to use for computations.
        """
        self.double_helices = np.ndarray((len(domains),), dtype=DoubleHelix)
        for index, domain in enumerate(domains.domains()):
            # When we instantiate a DoubleHelix, we need to pass an up and a down
            # helix, since every double helix must have exactly one of each. However,
            # the user inputs the generation counts (number of points to generate) for
            # the given helices based on the zeroedness of the helices--that is,
            # which helix is lined up to the right helix joint direction helix of the
            # previous domain.

            # Determine whether the zeroed helix is the up or down helix, and then
            # fetch the sum of the generation count for the helix. Then create the helix.
            zeroed_helix_direction = domain.left_helix_joint
            zeroed_helix_count = sum(domain.count_by_direction(zeroed_helix_direction))
            zeroed_helix = Helix(
                direction=zeroed_helix_direction, size=zeroed_helix_count, domain=domain
            )

            # Repeat the same steps as above for the helix with the opposite direction.
            other_helix_direction = inverse(zeroed_helix_direction)
            other_helix_count = sum(domain.count_by_direction(other_helix_direction))
            other_helix = Helix(
                direction=other_helix_direction, size=other_helix_count, domain=domain
            )

            # Create references to the helices based on their direction.
            up_helix = zeroed_helix if zeroed_helix.direction == UP else other_helix
            down_helix = zeroed_helix if zeroed_helix.direction == DOWN else other_helix

            # Create and store a DoubleHelix object that contains the two helices.
            self.double_helices[index] = DoubleHelix(domain, up_helix, down_helix)

        self.nucleic_acid_profile = nucleic_acid_profile

    def __len__(self) -> int:
        return len(self.double_helices)

    def __getitem__(self, index: int) -> "DoubleHelix":
        return self.double_helices[index]

    def __setitem__(self, index: int, value: DoubleHelix):
        self.double_helices[index] = value

    def __iter__(self) -> "DoubleHelix":
        return iter(self.double_helices)

    def domains(self) -> List["Domain"]:
        """
        Obtain all the domains of all the double helices in their respective order.

        Returns:
            A list of all the domains.
        """
        return [double_helix.domain for double_helix in self.double_helices]

    def compute(self):
        """
        Compute the point data for each helix.

        This computes the x coord, z coord, and angle arrays for each helix. The data
        is stored in the helices respective x coord, z coord, and angle arrays.
        """
        # Each domain (except the zeroth domain) is lined up such that the left side
        # of the domain lines up exactly with NEMids of the right side of the
        # previous domain; however, each domain still has two helices.

        # What we will do is compute the NEMids for the side of the domain that makes
        # a connection with the previous domain, and then we will compute the NEMids
        # for the other side of the domain later.

        for index, double_helix in enumerate(self):
            # Create a reference to the previous double helix
            previous_double_helix = self[index - 1]

            if index == 0:
                # The first domain is a special case. The z coord of the first NEMid
                # of the first domain is 0.
                initial_z_coord = 0
            else:
                # The initial z coord for all domains except the zeroth domain is the
                # z coordinate of the right-most point of the previous double helix's
                # right joint helix.
                initial_z_coord = previous_double_helix.right_helix.z_coords[
                    argmax(previous_double_helix.right_helix.x_coords)
                ]

                # Shift down the initial z coord. We can shift it down in increments
                # of Z_b * B, which we will call the "decrease_interval" (the
                # interval at which the z coord decreases).
                decrease_interval = (
                    self.nucleic_acid_profile.Z_b * self.nucleic_acid_profile.B
                )
                initial_z_coord -= (
                    ceil(initial_z_coord / decrease_interval) * decrease_interval
                )

            # We will compute the angles with numpy.arange(), which takes a start
            # value and a stop value, and increments by a step value. The start value
            # is 0, and the stop value is the number of points to generate times
            # theta_b + 1. We add +1 since it's ok if we generate extra points,
            # but we don't want any chance of missing a point due to being slightly
            # under the step value * theta_b. The step value is theta_b.
            angles = np.arange(
