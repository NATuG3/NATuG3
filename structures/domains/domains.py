import logging
from functools import cache
from typing import List, Iterable, Tuple, Literal, Type

import pandas as pd

import settings
from constants.directions import DOWN, UP
from structures.domains import Domain
from structures.domains.subunit import Subunit
from structures.domains.workers.side_view import DomainStrandWorker
from structures.domains.workers.top_view import TopViewWorker
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
        left_helix_count = [";".join(map(str, domain.left_helix_count)) for domain in domains]
        other_helix_count = [";".join(map(str, domain.other_helix_count)) for domain in domains]

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
        left_helix_count = [tuple(map(float, count.split(";"))) for count in data["Left Helix Count"].to_list()]
        other_helix_count = [tuple(map(float, count.split(";"))) for count in data["Other Helix Count"].to_list()]
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

    def clear_cache(self):
        """
        Clear the cache of all cached methods.

        Methods are cached because there is no need to recompute certain methods if the template subunit has
        not changed.
        """
        self.domains.cache_clear()
        self.subunits.cache_clear()

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
        logger.info(f"Replacing the template subunit with {new_subunit}.")
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

    @cache
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
        logger.debug(f"Fetched {len(output)} subunits.")
        return output

    @cache
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

        # set the proper indexes for all of the domains
        for index, domain in enumerate(output):
            output[index].index = index

        logger.debug(f"Fetched {len(output)} domains.")
        return output

    def points(self) -> List[Tuple[List[Point], List[Point]]]:
        """
        All the points in all the domains before they are turned into Strand objects.

        Returns:
            A list of tuples of points.

            The formatting of the points is a large list. Within that list lies a tuple for each domain.
            Within each tuple lies two lists. The first represents the up strand of that domain, and the
            second represents the down strand.

            This can be represented as:
            "AllDomains(Domain#0(up-strand, down-strand), Domain#1(up-strand, down-strand), ...)"
            Where up-strands and down-strands are lists of Point objects.

        Notes:
            This is a cached method. The cache is cleared when the subunit is changed.
        """
        if self._points is None:
            logger.debug("Recomputing points.")
            self._points = self.worker.compute()
        else:
            logger.debug("Using cached points.")
            return self._points

    @cache
    def strands(self) -> Strands:
        """
        Obtain a list of all strands from all workers.

        This is equivalent to utilizing the .points() method, and then placing all of those points into new Strand
        objects, and then calling Strands() on that list.

        This method automatically determines strand color based off of interdomain-ness, and uses the currently
        set nucleic acid nucleic_acid_profile for the strand's nucleic acid nucleic_acid_profile.

        Returns:
            A list of all strands from all workers.

        Notes:
            This is a cached method. The cache is cleared when the subunit is changed.
        """
        self._points = self.worker.compute()

        # Creating a list of strands, and then converting that list into a Strands object.
        listed_strands = []
        for domain in self.domains():
            for direction in (
                UP,
                DOWN,
            ):
                listed_strands.append(self._points[domain.index][direction])
        logger.debug(f"Fetched {len(listed_strands)} strands.")

        # ensure that the zeroth domain's up strand's first point is in the proper outputted strand
        assert self._points[0][0][0] in listed_strands[0]

        # ensure that the points are properly parented
        # check to see if the zeroth domain's up strand's first point's great-grandparent is us
        # Point.domain -> Domain
        # Domain.subunit -> Subunit
        # Subunit.domains -> Domains (should be us)
        assert self._points[0][0][0].domain.parent.parent is self

        # convert all items in listed_strands to Strand objects
        for index, strand in enumerate(listed_strands):
            listed_strands[index] = Strand(
                items=strand, color=settings.colors["sequencing"]["greys"][index % 2]
            )

        # convert sequencing from a list to a Strands container
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
