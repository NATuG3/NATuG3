from math import ceil
from typing import List, Iterator

import numpy as np
from numpy import argmax

from constants.directions import DOWN
from structures.points.point import x_coord_from_angle


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

    def __init__(self, domains: "Domains", nucleic_acid_profile) -> None:
        """
        Initialize a container for DoubleHelix objects.

        The size to make the data arrays of each helix is determined based on the
        domains' GenerationCounts.

        Args:
            domains: A Domains object containing the domains for the creation of the
                double helices. Each domain will be used to create a double helix,
                and the .domains() method will be used to fetch all the domains.
            nucleic_acid_profile: The nucleic acid profile to use for computations.
        """
        from structures.helices import DoubleHelix

        self.double_helices = [DoubleHelix(domain) for domain in domains.domains()]
        self.nucleic_acid_profile = nucleic_acid_profile

    def __len__(self) -> int:
        return len(self.double_helices)

    def __getitem__(self, index: int) -> "DoubleHelix":
        return self.double_helices[index]

    def __setitem__(self, index: int, value: "DoubleHelix"):
        self.double_helices[index] = value

    def __iter__(self) -> Iterator["DoubleHelix"]:
        return iter(self.double_helices)

    def domains(self) -> List["Domain"]:
        """
        Obtain all the domains of all the double helices in their respective order.

        Returns:
            A list of all the domains.
        """
        return [domain for domain in self.double_helices]

    def strands(self) -> "Strands":
        """
        Convert all the helices within the double helices within this container to
        strands, and package them within a Strands container.

        The .compute() method of this class must have been previously run for the
        data to be correct.

        Returns:
            A Strands container containing all the strands.
        """
        from structures.strands import Strands

        strands = []
        for double_helix in self:
            for helix in double_helix.helices:
                strands.append(helix.strand(self.nucleic_acid_profile))

        strands = Strands(
            strands=strands, nucleic_acid_profile=self.nucleic_acid_profile
        )
        strands.style()
        return strands

    def compute(self):
        """
        Compute the point data for each helix.

        This computes the x coord, z coord, and angle arrays for each helix. The data
        is stored in the helices respective x coord, z coord, and angle arrays.
        """
        from structures.domains import Domain

        def x_coords_from_angles(angles: np.ndarray, domain: Domain) -> np.ndarray:
            """
            Compute the x coords from the angles.

            Args:
                angles: The angles to use for the computation.

            Returns:
                The x coords.
            """
            return np.array([x_coord_from_angle(angle, domain) for angle in angles])

        for index, double_helix in enumerate(self):
            # Create a reference to the previous double helix
            previous_double_helix = self[index - 1]
            domain = double_helix.domain

            if index == 0:
                # The first domain is a special case. The z coord of the first NEMid
                # of the first domain is 0.
                aligned_z_coord = 0
            else:
                # The initial z coord for all domains except the zeroth domain is the
                # z coordinate of the right-most point of the previous double helix's
                # right joint helix.
                aligned_z_coord = previous_double_helix.right_helix.data.z_coords[
                    argmax(previous_double_helix.right_helix.data.x_coords)
                ]

                # Shift down the initial z coord. We can shift it down in increments
                # of Z_b * B, which we will call the "decrease_interval" (the
                # interval at which the z coord decreases).
                decrease_interval = (
                    self.nucleic_acid_profile.Z_b * self.nucleic_acid_profile.B
                )
                aligned_z_coord -= (
                    ceil(aligned_z_coord / decrease_interval) * decrease_interval
                )

            # Determine how many points (nucleosides/NEMids) the initial z coord
            # is below the x-axis. We are allowed to shift up the z coords so long as
            # we also increment the angles and x coords accordingly.
            if aligned_z_coord >= 0:
                shifts = 0
            else:
                shifts = round(
                    np.divide(abs(aligned_z_coord), self.nucleic_acid_profile.Z_b)
                )

            # Increment the starting z coord by the height between bases times the
            # number of shifts that we must apply to force the initial z coord to be
            # above the x-axis.
            aligned_z_coord += shifts * self.nucleic_acid_profile.Z_b
            # Since we've shifted the z coord, we must also shift the angle accordingly.
            aligned_angle = shifts * self.nucleic_acid_profile.theta_b
            # Note that the x coordinates are generated based off of the angles,
            # so we don't need to even define an "initial_x_coord" variable.

            # We must take into consideration the bottom_count of the zeroed helix.
            # The bottom count is how many more shifts down to go, on top of the
            # shifts that we've already applied. We will apply these shifts to the
            # initial z coord, and initial angle that we've just computed.
            increments = double_helix.zeroed_helix.domain.left_helix_count.bottom_count
            initial_z_coord = aligned_z_coord - (
                increments * self.nucleic_acid_profile.Z_b
            )
            initial_angle = aligned_angle - (
                increments * self.nucleic_acid_profile.theta_b
            )

            # Now we can determine the ending z coord and angle for the zeroed helix.
            # It is the domain's body_count plus the domain's top_count number of
            # increments up from the respective initial z coord and angle.
            increments = (
                double_helix.zeroed_helix.domain.left_helix_count.body_count
                + double_helix.zeroed_helix.domain.left_helix_count.top_count
            )
            final_z_coord = initial_z_coord + increments * self.nucleic_acid_profile.Z_b
            final_angle = initial_angle + increments * self.nucleic_acid_profile.theta_b

            # Compute the z coord and angle data for the zeroed helix; we will
            # generate the angles based off of the x coords later. Recall that we're
            # generating for the zeroed helix first because the initial z coord is
            # defined to be the z coord of the right-most point of the previous
            # double helix's right joint helix, which makes this domain's left helix
            # the zeroed helix.
            double_helix.zeroed_helix.data.z_coords = np.arange(
                start=initial_z_coord,
                stop=final_z_coord,
                step=self.nucleic_acid_profile.Z_b,
            )
            double_helix.zeroed_helix.data.angles = np.arange(
                start=initial_angle,
                stop=final_angle,
                step=self.nucleic_acid_profile.theta_b,
            )

            # The angles are computed based off of the x coords using the predefined
            # x_coord_from_angle function. The map() function returns a generator
            # that yields the x_coords_from_angle() function applied to each angle
            # one by one. Then we convert the generator to a numpy array.
            double_helix.zeroed_helix.data.x_coords = x_coords_from_angles(
                double_helix.zeroed_helix.data.angles, domain
            )

            # Now we will repeat the same process, but will shift the initial z coord
            # either down or up.
            if double_helix.other_helix.direction == DOWN:
                other_strand_modifier = -1
            else:
                other_strand_modifier = 1

            # Repeat the same process that we used for the zeroed strand of computing
            # the arange start and stop values based on domain's left_helix_count and
            # other_helix_count.

            # However, note that there is an offset this time for the z coords and
            # angles, which we must take into account.

            modifier = -1 if double_helix.other_helix.direction == DOWN else 1
            aligned_z_coord += modifier * self.nucleic_acid_profile.Z_mate
            aligned_angle += -modifier * self.nucleic_acid_profile.g

            increments = double_helix.zeroed_helix.domain.other_helix_count.bottom_count
            initial_angle = aligned_angle - (
                increments * self.nucleic_acid_profile.theta_b
            )
            initial_z_coord = aligned_z_coord - (
                increments * self.nucleic_acid_profile.Z_b
            )

            increments = (
                double_helix.zeroed_helix.domain.other_helix_count.body_count
                + double_helix.zeroed_helix.domain.other_helix_count.top_count
            )
            final_angle = initial_angle + increments * self.nucleic_acid_profile.theta_b
            final_z_coord = initial_z_coord + increments * self.nucleic_acid_profile.Z_b

            # Compute the z coord and angle data for the other helix.
            double_helix.other_helix.data.z_coords = np.arange(
                start=initial_z_coord,
                stop=final_z_coord,
                step=self.nucleic_acid_profile.Z_b,
            )
            double_helix.other_helix.data.angles = np.arange(
                start=initial_angle,
                stop=final_angle,
                step=self.nucleic_acid_profile.theta_b,
            )
            double_helix.other_helix.data.x_coords = x_coords_from_angles(
                double_helix.other_helix.data.angles, domain
            )
