import logging
from functools import cache
from typing import List, Iterable, Tuple, Literal

import pandas as pd

import settings
from constants.directions import DOWN, UP
from helpers import inverse
from structures.domains import Domain
from structures.domains.subunit import Subunit
from structures.domains.workers.side_view import DomainStrandWorker
from structures.domains.workers.top_view import TopViewWorker
from structures.points.point import Point
from structures.profiles import NucleicAcidProfile
from structures.strands import Strand, Strands

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
        domains: Iterable["Domain"],
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
        self._subunit = Subunit(self.nucleic_acid_profile, domains, template=True, parent=self)

        # create a worker object for computing strands for workers
        self.worker = DomainStrandWorker(self)
        self._points = None

    def to_file(self, mode: Literal["csv"], filepath: str) -> None:
        """
        Export all the current domains as a csv.

        Creates a csv file from self.domains() with the following columns:
            - left_helix_joint (if 0 then "UP" if 1 then "DOWN")
            - right_helix_joint (if 0 then "UP" if 1 then "DOWN")
            - s (which is based off left and right helix joints)
            - m (interior angle multiple)
            - count (number of points in the domain)

        Args:
            mode: The file type to export to. Must be in ("csv").
            filepath: The filepath to export to.

        Raises:
            ValueError: If the mode is not an allowed mode.
        """
        # extract all the data to references
        domains = self.domains()
        left_helix_joints = [domain.left_helix_joint for domain in domains]
        right_helix_joints = [domain.right_helix_joint for domain in domains]
        s = [domain.s for domain in domains]
        m = [domain.m for domain in domains]
        count = [domain.count for domain in domains]

        # create a pandas dataframe with the columns above
        data = pd.DataFrame(
            columns=["left_helix_joint", "right_helix_joint", "s", "m", "count"],
            data=[left_helix_joints, right_helix_joints, s, m, count],
        )

        # based on the mode chosen by the user, export the data to a file
        if mode == "csv":
            data.to_csv(filepath, index=False)
        else:  # if the mode is not one that is allowed, raise an error
            raise ValueError(f"Invalid mode: {mode}")

    @classmethod
    def from_file(cls, mode: Literal["csv"], filepath: str, nucleic_acid_profile: NucleicAcidProfile):
        """
        Import domains from a csv. Must be a csv in the format of self.to_file().

        Args:
            mode: The type of file being imported. Must be in ("csv").
            filepath: The filepath to import from.
            nucleic_acid_profile: The nucleic acid configuration.

        Returns:
            A Domains object.

        Raises:
            ValueError: If the mode is not an allowed mode.
        """
        # read the file based on the mode
        if mode == "csv":
            data = pd.read_csv(filepath)
        # if the mode is not one that is allowed, raise an error
        else:
            raise ValueError(f"Invalid mode: {mode}")

        # extract the data
        left_helix_joints = data["left_helix_joint"].to_list()
        right_helix_joints = data["right_helix_joint"].to_list()
        m = data["m"].to_list()
        count = data["count"].to_list()

        # create a list of domains
        domains = []
        for i in range(len(left_helix_joints)):
            domains.append(
                Domain(
                    nucleic_acid_profile,
                    left_helix_joint_direction=left_helix_joints[i],
                    right_helix_joint_direction=right_helix_joints[i],
                    theta_m_multiple=m[i],
                    count=count[i],
                )
            )

        # create a Domains object
        return cls(
            nucleic_acid_profile=settings.nucleic_acid_profile,
            domains=domains,
            symmetry=settings.symmetry,
            antiparallel=settings.antiparallel,
        )

    def clear_cache(self):
        """
        Clear the cache of all cached methods.
        """
        self.domains.cache_clear()
        self.subunits.cache_clear()
        self.points.cache_clear()

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
        """
        logger.info(f"Replacing the template subunit with {new_subunit}.")
        self._subunit = new_subunit
        for domain in self._subunit:
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
            # alternate from where we left off
            # (which is the very right end of the subunit workers)
            direction = self.subunit.domains[-1].right_helix_joint
            for domain in output:
                domain.left_helix_joint = direction
                domain.right_helix_joint = direction
                direction = inverse(direction)

        # set the proper indexes for all of the domains
        for index, domain in enumerate(output):
            output[index].index = index

        logger.debug(f"Fetched {len(output)} domains.")
        return output

    @cache
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
            self._points = self.worker.compute()
        logger.debug("Fetched points for domain")
        return self._points

    @cache
    def strands(self) -> Strands:
        """
        Obtain a list of all strands from all workers.

        This is equivalent to utilizing the .points() method, and then placing all of those points into new Strand
        objects, and then calling Strands() on that list.

        This method automatically determines strand color based off of interdomain-ness, and uses the currently
        set nucleic acid profile for the strand's nucleic acid profile.

        Returns:
            A list of all strands from all workers.

        Notes:
            This is a cached method. The cache is cleared when the subunit is changed.
        """
        self._points = self.worker.compute()

        # Creating a list of strands, and then converting that list into a Strands object.
        converted_strands = []
        for strand_direction in (
            UP,
            DOWN,
        ):
            # Creating a strand for each domain.
            for index, domain in enumerate(self.domains()):
                converted_strands.append(
                    Strand(
                        self.nucleic_acid_profile,
                        self._points[index][strand_direction],
                        color=settings.colors["sequencing"]["greys"][strand_direction],
                    )
                )
        logger.debug(f"Fetched {len(converted_strands)} strands.")
        # convert sequencing from a list to a Strands container
        return Strands(self.nucleic_acid_profile, converted_strands)

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
