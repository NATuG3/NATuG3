from collections import namedtuple
from math import dist
from typing import List, NamedTuple
import logging

import settings
from computers.side_view.strands.interface import Plotter
from computers.side_view.strands.strand import Strand
from datatypes.misc import Profile
from datatypes.points import NEMid

logger = logging.getLogger(__name__)


class Strands:
    def __init__(self, strands: List[Strand], profile: Profile) -> None:
        """
        Initialize an instance of Strands.

        Args:
            strands: A list of strands to create a Strands object from.
            profile: The settings profile to use for computations.
        """
        assert [isinstance(strand, Strand) for strand in strands]
        self.strands = strands

        assert isinstance(profile, Profile)
        self.profile = profile


    def add_junction(self, NEMid1: NEMid, NEMid2: NEMid) -> None:
        """
        Add a cross-strand junction where NEMid1 and NEMid2 overlap.

        Args:
            NEMid1: One NEMid at the junction site.
            NEMid2: Another NEMid at the junction site.

        Raises:
            ValueError: NEMids are ineligible to be made into a junction.
        """
        if dist(NEMid1.position(), NEMid2.position()) > settings.junction_threshold:
            raise ValueError(
                "NEMids are not close enough to create a junction.",
                NEMid1.position(),
                NEMid2.position()
            )
        if NEMid1.strand == NEMid2.strand:
            raise ValueError(
                "NEMids are on the same strand. Cannot create same-strand junction.",
                NEMid1.strand,
                NEMid2.strand
            )
        print("good")

    def ui(self) -> Plotter:
        return Plotter(
            self,
            self.size.width,
            self.size.height,
            self.profile
        )

    @property
    def size(self) -> NamedTuple("Size", width=float, height=float):
        """
        Obtain the size of all strands when laid out.

        Returns:
            tuple(width, height)
        """
        x_coords: List[float] = []
        z_coords: List[float] = []

        for strand in self.strands:
            strand: Strand
            for NEMid_ in strand:
                NEMid_: NEMid
                x_coords.append(NEMid_.x_coord)
                z_coords.append(NEMid_.z_coord)

        return namedtuple("Size", "width height")(
            max(x_coords) - min(x_coords),
            max(z_coords) - min(z_coords)
        )
