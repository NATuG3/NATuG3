import logging
import math
from time import time
from typing import List, Iterable, Tuple, Type

import pandas as pd
from xlsxwriter import Workbook

import settings
from constants.directions import DOWN, UP
from structures.domains import Domain
from structures.domains.subunit import Subunit
from structures.profiles import NucleicAcidProfile
from utils import inverse

logger = logging.getLogger(__name__)


class Domains:
    """
    Container for multiple domains.

    This is the strands of a Subunit, and the grandparent of a Domain.

    The Domains container automatically keeps track of a template subunit (created
    with domains passed through the init), and then automatically creates copies of
    that subunit and the domains in it when the .domains() method is called.

    Attributes:
        nucleic_acid_profile: The nucleic acid configuration.
        subunit: The domains within a single subunit.
            This is a template subunit. Note that subunits can be mutated.
        symmetry: The symmetry type. Also known as "R".
        count: The total number of domains. Includes domains from all subunits.
        antiparallel: Whether the domains are forced to have alternating
            upness/downness.

    Methods:
        strands: Returns a Strands object containing all the strands in the domains.
        top_view: Obtain a set of coords for the centers of all the double helices.
        domains: Returns a list of all domains.
        subunits: Returns a list of subunits.
        closed: Whether the tube is closed or not.
        update: Update the domains object in place.
        to_file: Write the domains to a file.
        from_file: Load a domains object from a file.
        write_worksheet: Write the domains to a tab in an Excel document.
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
            domains: All the domains for the template subunit.
            symmetry: The symmetry type. Also known as "R".
            antiparallel: Whether the domains are forced to have alternating
                upness/downness.
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
            assert domain.strands is self.subunit

    def __len__(self):
        return self.count

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
            domain.strands = self.subunit
        domains.subunit.parent = self

        # set attributes
        self.nucleic_acid_profile = domains.nucleic_acid_profile
        self.symmetry = domains.symmetry
        self.antiparallel = domains.antiparallel
        self.subunit = domains.subunit

    def to_file(self, filepath: str) -> None:
        """
        Export all the current domains as a csv.

        Creates a csv file from self.domains() with the following columns:
            Left Helix Joint ("UP" or "DOWN"): If 0 then "UP" if 1 then "DOWN"
            Right Helix Joint ("UP" or "DOWN"): If 0 then "UP" if 1 then "DOWN"
            Left Helix Count ("int:int:int"): The number of NEMids to add to the bottom
                of the left helix, followed by the number of NEMids to compute
                initially for the left helix, followed by the number of NEMids to add
                to the top of the left helix.
            Other Helix Count ("int:int:int"): Same as above but for the other helix.
            s: Which is based off left and right helix joints
            m: Interior angle multiple
            Symmetry (int): The symmetry type
            Antiparallel ("true" or "false"): Whether the domains are antiparallel

        Args:
            filepath: The filepath to export to.

        Raises:
            ValueError: If the mode is not an allowed mode or if the filepath contains
            an extension.

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
        theta_m_multiples = [domain.theta_m_multiple for domain in domains]
        symmetry = [self.symmetry, *[None for _ in range(len(domains) - 1)]]
        antiparallel = [self.antiparallel, *[None for _ in range(len(domains) - 1)]]
        left_helix_count = [
            "-".join(map(str, domain.left_helix_count)) for domain in domains
        ]
        other_helix_count = [
            "-".join(map(str, domain.other_helix_count)) for domain in domains
        ]

        # create a pandas dataframe with the columns above
        data = pd.DataFrame(
            {
                "m": theta_m_multiples,
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
            tuple(map(int, count.split("-")))
            for count in data["Left Helix Count"].to_list()
        ]
        other_helix_count = [
            tuple(map(int, count.split("-")))
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
                    left_helix_count=left_helix_count[i],  # type: ignore
                    other_helix_count=other_helix_count[i],  # type: ignore
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

    def write_worksheet(
        self, workbook: Workbook, name: str = "Domains", color: str = "#33CCCC"
    ):
        """
        Write the current domains to a tab in an Excel document.

        Args:
            workbook: The Excel spreadsheet to create a new tab for.
            name: The name of the tab.
            color: The color of the tab in the Excel spreadsheet.
        """
        # Add a tab for the domains to the workbook
        sheet = workbook.add_worksheet(name)
        sheet.set_tab_color(color)

        # Write the headers
        sheet.write(0, 0, "#")
        sheet.write(0, 1, "m")
        sheet.write(0, 2, "Left Helix Joints")
        sheet.write(0, 3, "Right Helix Joints")
        sheet.write(0, 4, "Left Helix Count (bottom)")
        sheet.write(0, 5, "Left Helix Count (initial)")
        sheet.write(0, 6, "Left Helix Count (top)")
        sheet.write(0, 7, "Other Helix Count (bottom)")
        sheet.write(0, 8, "Other Helix Count (initial)")
        sheet.write(0, 9, "Other Helix Count (top)")
        sheet.write(0, 10, "Symmetry")
        sheet.write(0, 11, "Antiparallel")

        # Write the data
        for i, domain in enumerate(self.domains(), start=1):
            sheet.write(i, 0, domain.index + 1)  # domain.index is index-0
            sheet.write(i, 1, domain.theta_m_multiple)
            sheet.write(i, 2, "UP" if domain.left_helix_joint == UP else "DOWN")
            sheet.write(i, 3, "UP" if domain.right_helix_joint == UP else "DOWN")
            sheet.write(i, 4, domain.left_helix_count[0])
            sheet.write(i, 5, domain.left_helix_count[1])
            sheet.write(i, 6, domain.left_helix_count[2])
            sheet.write(i, 7, domain.other_helix_count[0])
            sheet.write(i, 8, domain.other_helix_count[1])
            sheet.write(i, 9, domain.other_helix_count[2])

        # Symmetry and Antiparallelity have their own columns, but they only take up
        # one row.
        sheet.write(1, 10, self.symmetry)
        sheet.write(1, 11, self.antiparallel)

    def top_view(self) -> List[Tuple[float, float]]:
        """
        Create a set of coordinates that represent the top view of all the domains.

        Returns:
            A list of tuples containing the x and y coordinates of the domains.

        Notes:
            - The first element in the list is domain #0.
        """
        start_time = time()

        domains = self.domains()

        theta_deltas = [0.0]
        u_coords = [0.0]
        v_coords = [0.0]

        # Create references for various nucleic acid settings. This is done to make
        # the code more readable.
        D = self.nucleic_acid_profile.D

        for index, domain in enumerate(domains):
            # locate strand switch angle for the previous domain.
            theta_s: float = domains[index - 1].theta_s
            # locate interior angle for the previous domain.
            interior_angle_multiple: float = domains[index - 1].theta_m

            # calculate the actual interior angle (with strand switching angle
            # factored in)
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

        logger.info(
            "Performed top view computation in %s seconds.",
            round((time() - start_time), 4),
        )

        return list(zip(u_coords, v_coords))

    def closed(self):
        """
        Whether the Domains object is closed.

        This method determines if the (u, v) top view coordinate of the first domain
        is the same as the last domain. If they are the same then this is a closed
        DNA nanotube.

        Note that a threshold of settings.close_threshold is in case of real number
        errors. This just means that there is a small tolerance for a gap between the
        first and last domain's top view coord.
        """
        coords = self.top_view()
        return math.dist(coords[0], coords[-1]) < settings.closed_threshold

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
            domain.strands = self._subunit

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
        Obtain a list of all domains from all subunits.

        Returns:
            A list of all domains from all subunits.

        Notes:
            This is a cached method. The cache is cleared when the subunit is changed.
        """
        output = []
        for subunit in self.subunits():
            output.extend(subunit.domains)

        # if the domains instance is set to antiparallel then make the directions
        # of the domains alternate.
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

    def __repr__(self) -> str:
        """
        String representation of the Domains object.

        Returns the template subunit, symmetry, and antiparallel status.
        """
        return f"Domains(subunit={self.subunit}, symmetry={self.symmetry}, antiparallel={self.antiparallel})"
