import logging
import math
from functools import cache
from time import time
from typing import List, Iterable, Tuple, Literal, Type

import numpy as np
import pandas as pd

import settings
from constants.directions import DOWN, UP
from structures.domains import Domain
from structures.domains.subunit import Subunit
from structures.domains.workers.side_view import DomainStrandWorker
from structures.domains.workers.top_view import TopViewWorker
from structures.points import Nucleoside, NEMid
from structures.points.point import Point
from structures.profiles import NucleicAcidProfile
from structures.strands import Strand, Strands
from utils import inverse

logger = logging.getLogger(__name__)


class Domains:
    """
    Container for multiple workers.

    This is the parent of a Subunit, and the grandparent of a Domain.

    The Domains container automatically keeps track of a template subunit (created with domains
    passed through the init), and then automatically creates copies of that subunit and the
    domains in it when the .domains() method is called.

    Attributes:
        nucleic_acid_profile: The nucleic acid configuration.
        subunit: The workers within a single subunit.
            This is a template subunit. Note that subunits can be mutated.
        symmetry: The symmetry type. Also known as "R".
        count: The total number of workers. Includes workers from all subunits.
        antiparallel: Whether the workers are forced to have alternating upness/downness.

    Methods:
        strands()
        top_view()
        workers()
        subunits()
    """

    def __init__(
        self,
        nucleic_acid_profile: NucleicAcidProfile,
        domains: List[Domain],
        symmetry: int,
        antiparallel: bool = False,
    ) -> None:
        """
        Initialize a Domains object.

        Args:
            nucleic_acid_profile: The nucleic acid configuration.
            domains: All the workers for the template subunit.
            symmetry: The symmetry type. Also known as "R".
            antiparallel: Whether the workers are forced to have alternating upness/downness.
        """
        # store various settings
        self.nucleic_acid_profile = nucleic_acid_profile
        self.symmetry = symmetry
        self.antiparallel = antiparallel

        # self.subunit is the template subunit
        # meaning that all other subunits are based off of this one
        assert isinstance(domains, Iterable)
        self._subunit = Subunit(
            self.nucleic_acid_profile, domains, template=True, parent=self
        )
        for domain in self.subunit.domains:
            assert domain.parent is self.subunit

        # create a worker object for computing strands for workers
        self.worker = DomainStrandWorker(self)
        self._points = None

    def update(self, domains: Type["Domains"]) -> None:
        """
        Update the domains object in place.

        Sets all of our attributes with the attributes of a different domains object.

        Args:
            domains: The domains object to update with.

        Raises:
            ValueError: If the domains object is not a Domains object.

        Notes:
            - This method clears the cache.
        """
        if not isinstance(domains, Domains):
            raise ValueError("Domains object must be a Domains object.")

        # set parents
        for domain in domains.subunit.domains:
            domain.parent = self.subunit
        domains.subunit.parent = self

        # set attributes
        self.nucleic_acid_profile = domains.nucleic_acid_profile
        self.symmetry = domains.symmetry
        self.antiparallel = domains.antiparallel
        self.subunit = domains.subunit

        # create a worker
        self.worker = DomainStrandWorker(self)

        # clear cache
        self.clear_cache()

    def to_file(self, filepath: str) -> None:
        """
        Export all the current domains as a csv.

        Creates a csv file from self.domains() with the following columns:
            Left Helix Joint ("UP" or "DOWN"): If 0 then "UP" if 1 then "DOWN"
            Right Helix Joint ("UP" or "DOWN"): If 0 then "UP" if 1 then "DOWN"
            Left Helix Count ("int:int:int"): The number of NEMids to add to the bottom of the left helix, followed by
                the number of NEMids to compute initially for the left helix, followed by the number of NEMids to add to
                the top of the left helix.
            Other Helix Count ("int:int:int"): Same as above but for the other helix.
            s: Which is based off left and right helix joints
            m: Interior angle multiple
            Symmetry (int): The symmetry type
            Antiparallel ("true" or "false"): Whether the domains are antiparallel

        Args:
            filepath: The filepath to export to.

        Raises:
            ValueError: If the mode is not an allowed mode or if the filepath contains an extension.

        Notes:
            - Filetype is determined by the extension.
            - Supported filetypes: csv
        """
        # extract all the data to references
        domains = self.subunit.domains
        left_helix_joints = [
            "UP" if domain.left_helix_joint == UP else "DOWN" for domain in domains
        ]
        right_helix_joints = [
            "UP" if domain.right_helix_joint == UP else "DOWN" for domain in domains
        ]
        m = [domain.theta_interior_multiple for domain in domains]
        symmetry = [self.symmetry, *[None for _ in range(len(domains) - 1)]]
        antiparallel = [self.antiparallel, *[None for _ in range(len(domains) - 1)]]
        left_helix_count = [
            ";".join(map(str, domain.left_helix_count)) for domain in domains
        ]
        other_helix_count = [
            ";".join(map(str, domain.other_helix_count)) for domain in domains
        ]

        # create a pandas dataframe with the columns above
        data = pd.DataFrame(
            {
                "m": m,
                "Left Helix Joints": left_helix_joints,
                "Right Helix Joints": right_helix_joints,
                "Left Helix Count": left_helix_count,
                "Other Helix Count": other_helix_count,
                "Symmetry": symmetry,
                "Antiparallel": antiparallel,
            },
        )

        # based on the mode chosen by the user, export the data to a file
        if filepath.endswith("csv"):
            data.to_csv(filepath, index=False)
        else:  # if the mode is not one that is allowed, raise an error
            raise ValueError(f"Invalid mode: {filepath[filepath.find('.'):]}")

    @classmethod
    def from_file(
        cls,
        filepath: str,
        nucleic_acid_profile: NucleicAcidProfile,
    ):
        """
        Import domains from a csv. Must be a csv in the format of self.to_file().

        Args:
            filepath: The filepath to import from.
            nucleic_acid_profile: The nucleic acid configuration.

        Returns:
            A Domains object.

        Notes:
            - Filetype is determined by the extension.
        """
        # read the file based on the mode
        if filepath.endswith("csv"):
            data = pd.read_csv(filepath)
        # if the mode is not one that is allowed, raise an error
        else:
            raise ValueError(f"Invalid mode: {filepath[filepath.find('.'):]}")

        # extract the data
        left_helix_joints = [
            UP if direction == "UP" else DOWN
            for direction in data["Left Helix Joints"].to_list()
        ]
        right_helix_joints = [
            UP if direction == "UP" else DOWN
            for direction in data["Right Helix Joints"].to_list()
        ]
        m = [int(m) for m in data["m"].to_list()]
        left_helix_count = [
            tuple(map(int, count.split(";")))
            for count in data["Left Helix Count"].to_list()
        ]
        other_helix_count = [
            tuple(map(int, count.split(";")))
            for count in data["Other Helix Count"].to_list()
        ]
        symmetry = int(data["Symmetry"].to_list()[0])
        antiparallel = data["Antiparallel"].to_list()[0]

        # create a list of domains
        domains = []
        for i in range(len(left_helix_joints)):
            domains.append(
                Domain(
                    nucleic_acid_profile=nucleic_acid_profile,
                    theta_m_multiple=m[i],
                    left_helix_joint=left_helix_joints[i],
                    right_helix_joint=right_helix_joints[i],
                    left_helix_count=left_helix_count[i],
                    other_helix_count=other_helix_count[i],
                )
            )

        # create a Domains object
        domains = cls(
            nucleic_acid_profile=nucleic_acid_profile,
            domains=domains,
            symmetry=symmetry,
            antiparallel=antiparallel,
        )

        return domains

    def top_view(self) -> List[Tuple[float, float]]:
        """
        Get the top view of the domains.

        Returns:
            A list of tuples containing the x and y coordinates of the domains.

        Notes:
            - The first element in the list is the leftmost domain.
        """
        domains = self.domains()

        theta_deltas = []
        u_coords = []
        v_coords = []

        # Create references for various nucleic acid settings. This is done to make the code more readable.
        theta_s = self.nucleic_acid_profile.theta_s
        theta_c = self.nucleic_acid_profile.theta_c
        D = self.nucleic_acid_profile.D

        for index, domain in enumerate(domains):
            # locate strand switch angle for the previous domain.
            theta_s: float = domains[index - 1].theta_s_multiple * theta_s
            # locate interior angle for the previous domain.
            interior_angle_multiple: float = (
                domains[index - 1].theta_interior_multiple * theta_c
            )

            # calculate the actual interior angle (with strand switching angle factored in)
            interior_angle: float = interior_angle_multiple - theta_s

            # append the angle change to "self.angle_deltas"
            theta_deltas.append(theta_deltas[-1] + 180 - interior_angle)

            # the current angle delta (we will use it to generate the next one)
            angle_delta: float = theta_deltas[-1]
            angle_delta: float = math.radians(
                angle_delta
            )  # convert to radians (AKA angle_delta*(180/pi))

            # append the u cord of the domain to "self.u_coords"
            u_coords.append(u_coords[-1] + D * math.cos(angle_delta))

            # append the v cord of the domain to "self.v_coords"
            v_coords.append(v_coords[-1] + D * math.sin(angle_delta))

        logger.debug("Performed top view computation.")

        return list(zip(u_coords, v_coords))

    @property
    def subunit(self) -> Subunit:
        """
        Obtain the current template subunit.

        Returns:
            The current template subunit.
        """
        return self._subunit

    @subunit.setter
    def subunit(self, new_subunit) -> None:
        """
        Replace the current template subunit.

        Args:
            new_subunit: The new template subunit.

        Notes:
            This method clears the cache of all cached methods.
        """
        logger.info(f"Replacing the template subunit.")
        self._subunit = new_subunit
        for domain in self._subunit.domains:
            domain.parent = self._subunit
        self.clear_cache()

    @property
    def count(self) -> int:
        """
        The number of workers in the Domains object.

        Returns:
            The number of workers in the Domains object.
        """
        return len(self.domains())

    def subunits(self) -> List[Subunit]:
        """
        Obtain all subunits of the Domains object.

        Returns:
            List[Subunit]: Copies of the template subunit for all subunits except the first one.
            The first subunit in the returned list is a direct reference to the template subunit.

        Notes:
            This is a cached method. The cache is cleared when self.subunit is changed.
        """
        output = []
        for cycle in range(self.symmetry):
            # for all subunits after the first one make deep copies of the subunit.
            if cycle == 0:
                output.append(self.subunit)
            else:
                copied = self.subunit.copy()
                copied.template = False
                output.append(copied)
        return output

    def domains(self) -> List["Domain"]:
        """
        Obtain a list of all workers from all subunits.

        Returns:
            A list of all workers from all subunits.

        Notes:
            This is a cached method. The cache is cleared when the subunit is changed.
        """
        output = []
        for subunit in self.subunits():
            output.extend(subunit.domains)

        # if the workers instance is set to antiparallel then make the directions
        # of the workers alternate.
        if self.antiparallel:
            # begin with UP
            direction = UP
            for domain in output:
                domain.left_helix_joint = direction
                domain.right_helix_joint = direction
                direction = inverse(direction)

        # set the proper indexes for all the domains
        for index, domain in enumerate(output):
            output[index].index = index

        return output

    def strands(self) -> Strands:
        """
        Generate a list of all from the current domains.

        Creates and lines up strands for junctions.

        Returns:
            A list of all strands from all workers.

        Notes:
            This is a cached method. The cache is cleared when the subunit is changed.
        """
        # Store the time so that we can output the duration
        start_time = time()

        # Obtain the domains needed
        domains: List[Domain] = self.domains()

        # Each domain (except the zeroth domain) is lined up such that the left side of the domain lines up exactly
        # with NEMids of the right side of the previous domain; however, each domain still has two helices.

        # What we will do is compute the NEMids for the side of the domain that makes a connection with the
        # previous domain, and then we will compute the NEMids for the other side of the domain later.

        # Create an empty container for the strands of the up and down strand of each domain. The structure here is
        # a list of tuples, where each tuple is a pair of strands (one for the up strand and one for the down strand).
        # Each strand is a list of NEMid and Nucleoside objects.
        strands: List[Tuple[Strand, Strand]]
        strands = [
            (
                Strand(),
                Strand(),
            )
            for domain in domains
        ]

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
        for domain in domains:
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
                initial_z_coord = all_zeroed_strand_z_coords[-1][
                    np.argmax(all_zeroed_strand_x_coords[-1])
                ]
                # Shift down the initial z coord. We can shift it down in increments of Z_b * B, which we will call the
                # "decrease_interval" (the interval at which the z coord decreases).
                decrease_interval = Z_b * B
                initial_z_coord -= (
                    np.ceil(initial_z_coord / decrease_interval) * decrease_interval
                )

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
                theta_b / 2,  # the amount to step by for each angle
            )
            all_zeroed_strand_angles.append(zeroed_strand_angles)

            # Generate all the x coords. X coords are generated based off of the angles, so we will use map
            # Point.x_coord_from_angle onto a copy of current_angles.
            zeroed_strand_x_coords = np.array(
                [
                    Point.x_coord_from_angle(angle, domain)
                    for angle in zeroed_strand_angles
                ]
            )
            all_zeroed_strand_x_coords.append(zeroed_strand_x_coords)

            # Generate all the z coords. We begin at z=0 and step by Z_b/2 for domain.left_helix_count[1] times. Note
            # that we are generating the data for NEMids and Nucleosides, which is why we step by half a Z_b.
            zeroed_strand_z_coords = np.arange(
                initial_z_coord,  # when to start generating z coords
                final_z_coord,  # when to stop generating z coords
                Z_b / 2,  # the amount to step by for each z coord
            )
            all_zeroed_strand_z_coords.append(zeroed_strand_z_coords)

            # Now, using various attributes of the nucleic acid profile, we can easily compute the other_strand (the
            # strand that does not make a connection with the previous domain).
            other_strand_angles = zeroed_strand_angles + self.nucleic_acid_profile.g
            other_strand_x_coords = np.array(
                [
                    Point.x_coord_from_angle(angle, domain)
                    for angle in other_strand_angles
                ]
            )
            other_strand_z_coords = (
                zeroed_strand_z_coords + self.nucleic_acid_profile.Z_mate
            )

            zeroed_strand_data = zip(
                zeroed_strand_x_coords, zeroed_strand_z_coords, zeroed_strand_angles
            )
            other_strand_data = zip(
                other_strand_x_coords, other_strand_z_coords, other_strand_angles
            )

            # Build the list of NEMid and Nucleosides objects to append to the strands container for the zeroed strand.
            for counter, (x_coord, z_coord, angle) in enumerate(zeroed_strand_data):
                if counter % 2:
                    # If the counter is odd, we are generating a NEMid.
                    zeroed_strand_NEMid = NEMid(
                        x_coord=x_coord, z_coord=z_coord, angle=angle
                    )
                    strands[domain.index][zeroed_strand_direction].append(
                        zeroed_strand_NEMid
                    )
                else:
                    # If the counter is even, we are generating a Nucleoside.
                    zeroed_strand_nucleoside = Nucleoside(
                        x_coord=x_coord, z_coord=z_coord, angle=angle
                    )
                    strands[domain.index][zeroed_strand_direction].append(
                        zeroed_strand_nucleoside
                    )
            # Build the list of NEMid and Nucleosides objects to append to the strands container for the other strand.
            for counter, (x_coord, z_coord, angle) in enumerate(other_strand_data):
                if counter % 2:
                    # If the counter is odd, we are generating a NEMid.
                    other_strand_NEMid = NEMid(
                        x_coord=x_coord, z_coord=z_coord, angle=angle
                    )
                    strands[domain.index][other_strand_direction].append(
                        other_strand_NEMid
                    )
                else:
                    # If the counter is even, we are generating a Nucleoside.
                    other_strand_nucleoside = Nucleoside(
                        x_coord=x_coord, z_coord=z_coord, angle=angle
                    )
                    strands[domain.index][other_strand_direction].append(
                        other_strand_nucleoside
                    )

            # Now that we have computed all of the base NEMids we can compute the extra lower and uppper NEMids.
            # The additional NEMids to place on top for each strand are count[2] and the additional NEMids to place
            # on the bottom are count[0]. Recall that count[1] is the number of NEMids to generate initially.
            strands[domain.index][zeroed_strand_direction].generate_NEMids(
                zeroed_strand_NEMid_count[0],
                domain,
                direction=DOWN,
            )
            strands[domain.index][zeroed_strand_direction].generate_NEMids(
                zeroed_strand_NEMid_count[2],
                domain,
                direction=UP,
            )

            # Assign the domain and direction to all the NEMids and Nucleosides in the strands.
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
            round((time() - start_time), 4),
        )

        return Strands(self.nucleic_acid_profile, listed_strands)

    def top_view(self) -> TopViewWorker:
        """
        Obtain a TopViewWorker object of all the domains. The top view worker object (which is located at
        structures/domains/workers/top_view-TopViewWorker()). This object contains various properties relavent
        to a top view plot, including coordinates, angle deltas, and more.

        Returns:
            A TopViewWorker object.

        Notes:
            This function is not cached; however, top view computation is a fairly inexpensive process.
        """
        logger.debug("Fetched a TopViewWorker object.")
        return TopViewWorker(self)

    def __repr__(self) -> str:
        """
        String representation of the Domains object.

        Returns the template subunit, symmetry, and antiparallel status.
        """
        return f"Domains(subunit={self.subunit}, symmetry={self.symmetry}, antiparallel={self.antiparallel})"
