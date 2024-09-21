import logging
import math
from contextlib import suppress
from copy import copy
from typing import Iterable, List

import numpy as np
import pandas as pd
from xlsxwriter import Workbook

from natug import settings
from natug.constants.directions import DOWN, UP
from natug.structures.domains import Domain
from natug.structures.domains.subunit import Subunit
from natug.structures.profiles import NucleicAcidProfile
from natug.utils import timer

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
        destroy_symmetry: Destroy the symmetry of the domains.
        invert: Invert two domains deeper into the nanotube.
        subunits: Returns a list of subunits.
        closed: Whether the tube is closed or not.
        update: Update the domains object in place.
        to_df: Export the domains to a dataframe.
        from_df: Import the domains from a dataframe.
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
            domain.parent = self.subunit

    def __len__(self):
        return self.count

    def update(self, domains: "Domains") -> None:
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

    def to_df(self, include_uuid: bool = True) -> pd.DataFrame:
        """
        Export all the current domains as a pandas dataframe.

        Creates a pandas dataframe representing the Domains with the following columns:
            * uuid: The unique identifier for the domain. Only included if
                <include_uuid> is True.
            * Left Helix Joint ("UP" or "DOWN"): If 0 then "UP" if 1 then "DOWN"
            * Right Helix Joint ("UP" or "DOWN"): If 0 then "UP" if 1 then "DOWN"
            * Up helix count ("int:int:int"): The amount of initial Nucleosides to
                generate for the up helix of a given domain.
            * Down helix count ("int:int:int"): The amount of initial Nucleosides to
                generate for the up helix of a given domain.
            * s: Which is based off left and right helix joints
            * m: Interior angle multiple
            * Symmetry (int): The symmetry type
            * Antiparallel ("true" or "false"): Whether the domains are antiparallel

        Returns:
            A pandas dataframe containing the domains' data.
        """
        # extract all the data and compile it into lists
        domains = self.subunit.domains
        uuids = [domain.uuid for domain in domains]
        left_helix_joints = [
            "UP" if domain.left_helix_joint == UP else "DOWN" for domain in domains
        ]
        right_helix_joints = [
            "UP" if domain.right_helix_joint == UP else "DOWN" for domain in domains
        ]
        theta_m_multiples = [domain.theta_m_multiple for domain in domains]
        symmetry = [self.symmetry, *[None for _ in range(len(domains) - 1)]]
        antiparallel = [self.antiparallel, *[None for _ in range(len(domains) - 1)]]
        up_helix_counts = [
            "&".join(map(str, domain.up_helix_count)) for domain in domains
        ]
        down_helix_counts = [
            "&".join(map(str, domain.down_helix_count)) for domain in domains
        ]

        # Create a dictionary with the columns above, and the UUIds only if requested
        data = {
            "data:m": theta_m_multiples,
            "data:left_helix_joints": left_helix_joints,
            "data:right_helix_joints": right_helix_joints,
            "data:up_helix_counts": up_helix_counts,
            "data:down_helix_counts": down_helix_counts,
            "data:symmetry": symmetry,
            "data:antiparallel": antiparallel,
        }
        if include_uuid:
            data["uuid"] = uuids

        # Create a pandas dataframe with the columns above
        return pd.DataFrame(data)

    @classmethod
    def dummy(cls, nucleic_acid_profile: NucleicAcidProfile):
        """An arbitrary minimal Domains object."""
        fake_domains = []
        for i in range(2):
            fake_domains.append(
                Domain(nucleic_acid_profile, 4, 0, 0, (1, 1, 1), (1, 1, 1), index=i)
            )
        return cls(nucleic_acid_profile, fake_domains, 1, False)

    @classmethod
    def from_df(
        cls,
        df: pd.DataFrame,
        nucleic_acid_profile: NucleicAcidProfile,
    ):
        """
        Import domains from a pandas dataframe. The dataframe must match the format
        of the dataframe created by the to_df method.

        Args:
            df: The dataframe to import from.
            nucleic_acid_profile: The nucleic acid configuration to load into the
                newly created Domains object.

        Returns:
            A Domains object.
        """
        # Extract the data from the dataframe
        uuids = df["uuid"].to_list() if "uuid" in df.columns else None
        left_helix_joints = [
            UP if direction == "UP" else DOWN
            for direction in df["data:left_helix_joints"].to_list()
        ]
        right_helix_joints = [
            UP if direction == "UP" else DOWN
            for direction in df["data:right_helix_joints"].to_list()
        ]
        m = [int(m) for m in df["data:m"].to_list()]
        up_helix_counts = [
            tuple(map(int, count.split("&")))
            for count in df["data:up_helix_counts"].to_list()
        ]
        down_helix_counts = [
            tuple(map(int, count.split("&")))
            for count in df["data:down_helix_counts"].to_list()
        ]
        symmetry = int(df["data:symmetry"].to_list()[0])
        antiparallel = df["data:antiparallel"].to_list()[0]

        # create a list of domains
        domains = []
        for i in range(len(left_helix_joints)):
            domains.append(
                Domain(
                    index=i,
                    uuid=uuids[i] if uuids else None,
                    nucleic_acid_profile=nucleic_acid_profile,
                    theta_m_multiple=m[i],
                    left_helix_joint=left_helix_joints[i],
                    right_helix_joint=right_helix_joints[i],
                    up_helix_count=up_helix_counts[i],  # type: ignore
                    down_helix_count=down_helix_counts[i],  # type: ignore
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
        sheet.write(0, 4, "Up Helix Count (bottom)")
        sheet.write(0, 5, "Up Helix Count (initial)")
        sheet.write(0, 6, "Up Helix Count (top)")
        sheet.write(0, 7, "Down Helix Count (bottom)")
        sheet.write(0, 8, "Down Helix Count (initial)")
        sheet.write(0, 9, "Down Helix Count (top)")
        sheet.write(0, 10, "Symmetry")
        sheet.write(0, 11, "Antiparallel")

        # Write the data
        for i, domain in enumerate(self.domains(), start=1):
            sheet.write(i, 0, domain.index + 1)  # domain.index is index-0
            sheet.write(i, 1, domain.theta_m_multiple)
            sheet.write(i, 2, "UP" if domain.left_helix_joint == UP else "DOWN")
            sheet.write(i, 3, "UP" if domain.right_helix_joint == UP else "DOWN")
            sheet.write(i, 4, domain.up_helix_count[0])
            sheet.write(i, 5, domain.up_helix_count[1])
            sheet.write(i, 6, domain.up_helix_count[2])
            sheet.write(i, 7, domain.down_helix_count[0])
            sheet.write(i, 8, domain.down_helix_count[1])
            sheet.write(i, 9, domain.down_helix_count[2])

        # Symmetry and Antiparallelity have their own columns, but they only take up
        # one row.
        sheet.write(1, 10, self.symmetry)
        sheet.write(1, 11, self.antiparallel)

    @timer(logger=logger, task_name="Domains top view computation")
    def top_view(self) -> np.ndarray:
        """
        Create a set of coordinates that represent the top view of all the domains.

        Returns:
            A numpy array of (u, v) coordinates for each domain. An additional coordinate
                is added for a hypothetical self.count+1th domain, so that the direction
                that the last domain trails off in is accessible. Also, an additional
                coordinate is prepended to the array to represent the origin entry
                direction.
        """
        domains = self.domains()
        coords = np.zeros((self.count + 2, 2))
        diameter = self.nucleic_acid_profile.D

        coords[0] = (
            -diameter * math.cos(math.radians(180 + domains[0].theta_i)),
            -diameter * math.sin(math.radians(180 + domains[0].theta_i)),
        )
        # coords[1] = (0, 0) (this is the default)
        coords[2] = (diameter, 0)
        absolute_angle = 180 - domains[1].theta_i

        for index in range(3, self.count + 2):
            coords[index] = (
                coords[index - 1][0]
                + diameter * math.cos(math.radians(absolute_angle)),
                coords[index - 1][1]
                + diameter * math.sin(math.radians(absolute_angle)),
            )
            with suppress(IndexError):
                absolute_angle += 180 - domains[index - 1].theta_i

        return coords

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
        return math.dist(coords[0], coords[-2]) < settings.closed_threshold

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
        for domain in self._subunit:
            domain.parent = self._subunit

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
        # Sometimes the user will set up the domains such that alternating subunits need
        # to be inverted to allow for a closed tube. In this case auto_antiparallel will
        # be True. (both requested (first condition) and needed (second condition))
        auto_antiparallel = (
            self.antiparallel
            and self.subunit[0].left_helix_joint == self.subunit[-1].right_helix_joint
        )

        output = []
        for cycle in range(self.symmetry):
            # For all subunits after the first one make deep copies of the subunit.
            if cycle == 0:
                output.append(self.subunit)
            else:
                copied = self.subunit.copy()
                if auto_antiparallel and cycle % 2:
                    copied = copied.inverted()
                copied.template = False
                output.append(copied)

        return output

    def domains(self) -> List["Domain"]:
        """
        Obtain a list of all domains from all subunits.

        Returns:
            A list of all domains from all subunits.
        """
        # If the structure is nonsymmetrical then self.subunit.domains := self.domains()
        if self.symmetry == 1:
            return self.subunit.domains

        # Get all the domains from all the subunits
        output = []
        for subunit in self.subunits():
            output.extend(subunit.domains.copy())

        # Set the proper indexes for all the domains
        for index, domain in enumerate(output):
            output[index].index = index

        return output

    def destroy_symmetry(self) -> None:
        """
        Make the Domains non-symmetrical by setting symmetry to 1 and applying the angles
        that are a result of the current symmetry setting.
        """
        if self.symmetry != 1:
            self.subunit = Subunit(
                self.nucleic_acid_profile,
                self.domains(),
                template=True,
                parent=self,
            )
            for index, domain in enumerate(self.subunit):
                domain.index = index
            self.symmetry = 1

    def invert(self, domain1: Domain, domain2: Domain) -> None:
        """
        Invert two domains deeper into the nanotube.

        Args:
            domain1: The first domain of the two that are to be inverted into the tube.
            domain2: The second domain of the two that are to be inverted into the tube.

        Notes:
            Symmetry of the tube is destroyed first. Current symmetrical settings are
            applied to the tube and the symmetry factor is changed to 1-fold-symmetry.
        """
        # Apply the domain inversion formula:
        # let b be the number of bases per t turns for the nucleic acid
        #   A -> A - [b - (B + C)] = A + B + C - b
        #   B -> 21 - C
        #   C -> 21 - B
        #   D -> D - [b - (B + C)] = D + B + C - b
        # Where the letters refer to the interior angle multiples of domain A, B, C, D.
        self.destroy_symmetry()

        # Since there's only one subunit, self.domains() := self.subunit.domains
        domain_A: Domain = copy(self.subunit[domain1.index - 1 % len(self)])
        domain_B: Domain = copy(domain1)
        domain_C: Domain = copy(domain2)
        domain_D: Domain = copy(self.subunit[(domain2.index + 1) % len(self)])

        self.subunit[domain1.index - 1].theta_m_multiple = (
            domain_A.theta_m_multiple
            + domain_B.theta_m_multiple
            + domain_C.theta_m_multiple
            - self.nucleic_acid_profile.B
        )
        self.subunit[domain1.index].theta_m_multiple = (
            self.nucleic_acid_profile.B - domain_C.theta_m_multiple
        )
        self.subunit[domain2.index].theta_m_multiple = (
            self.nucleic_acid_profile.B - domain_B.theta_m_multiple
        )
        self.subunit[(domain2.index + 1) % len(self)].theta_m_multiple = (
            domain_D.theta_m_multiple
            + domain_B.theta_m_multiple
            + domain_C.theta_m_multiple
            - self.nucleic_acid_profile.B
        )

    def __repr__(self) -> str:
        """
        String representation of the Domains object.

        Returns the template subunit, symmetry, and antiparallel status.
        """
        return f"Domains(subunit={self.subunit}, symmetry={self.symmetry}, antiparallel={self.antiparallel})"
