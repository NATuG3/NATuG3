from collections import namedtuple
from math import dist
from typing import List, NamedTuple
import logging

import settings
from constants.directions import *
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


        NEMid1_strand_index = self.strands.index(NEMid1.strand)
        NEMid2_strand_index = self.strands.index(NEMid2.strand)
        insert_at = NEMid1_strand_index

        # remove the strands that we are going to replace with 4 new strands
        del self.strands[NEMid1_strand_index]
        del self.strands[NEMid2_strand_index-1]

        new_strands = [
            Strand(
                [], color=(110, 255, 117)
            ), Strand(
                [], color=(250, 145, 255)
            )
        ]

        for NEMid_ in NEMid1.strand:
            if NEMid1.domain.helix_joints[RIGHT] == UP:
                if NEMid_.z_coord < NEMid1.z_coord:
                    new_strands[0].append(NEMid_)
            else:  # NEMid1.domain.helix_joints[DOWN]:
                if NEMid_.z_coord > NEMid1.z_coord:
                    new_strands[0].append(NEMid_)

        for NEMid_ in NEMid2.strand:
            if NEMid2.domain.helix_joints[LEFT] == UP:
                if NEMid_.z_coord < NEMid2.z_coord:
                    new_strands[1].append(NEMid_)
            else:  # NEMid1.domain.helix_joints[DOWN]:
                if NEMid_.z_coord > NEMid2.z_coord:
                    new_strands[1].append(NEMid_)


        self.strands.insert(insert_at, new_strands[0])
        self.strands.insert(insert_at+1, new_strands[1])



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
