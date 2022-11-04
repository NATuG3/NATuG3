import logging
import sys
from collections import namedtuple
from copy import copy, deepcopy
from math import dist
from typing import List, NamedTuple

import settings
from structures.misc import Profile
from structures.points import NEMid
from structures.strands.strand import Strand

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

        self.previous_strands = {}

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
                NEMid2.position(),
            )

        # ensure that NEMid1 is the lefter NEMid
        if NEMid1.x_coord > NEMid2.x_coord:
            NEMid1, NEMid2 = NEMid2, NEMid1

        if NEMid1.strand is not NEMid2.strand:
            new_strands = [Strand([], color=(255, 0, 0)), Strand([], color=(0, 255, 0))]
            alt_colors = {
                (255, 0, 0): (10, 255, 255),
                (10, 255, 255): (255, 0, 0),
                (0, 0, 255): (0, 255, 0),
                (0, 255, 0): (0, 0, 255)
            }

            # first new strand
            for NEMid_ in tuple(NEMid1.strand)[: NEMid1.index() + 1]:
                new_strands[0].append(copy(NEMid_))
            #
            for NEMid_ in tuple(NEMid2.strand)[NEMid2.index() + 1:]:
                new_strands[0].append(copy(NEMid_))

            # second new strand
            for NEMid_ in tuple(NEMid2.strand)[: NEMid2.index() + 1]:
                new_strands[1].append(copy(NEMid_))
            #
            for NEMid_ in tuple(NEMid1.strand)[NEMid1.index() + 1:]:
                new_strands[1].append(copy(NEMid_))

            # store hashes of the previous strands in case undoes strand in future
            self.previous_strands[(hash(tuple(NEMid1.strand)))] = NEMid1.strand.color
            self.previous_strands[(hash(tuple(NEMid2.strand)))] = NEMid2.strand.color

            self.strands.remove(NEMid1.strand)
            self.strands.remove(NEMid2.strand)

            for new_strand in new_strands:
                for existing_strand in self.strands:
                    existing_strand_location = existing_strand.location
                    new_strand_location = new_strand.location
                    for check in range(4):
                        if abs(
                                existing_strand_location[check]-new_strand_location[check]
                        ) < .5:
                            if not existing_strand.greyscale:
                                new_strand.color = alt_colors[new_strand.color]

                if hash(tuple(new_strand)) in self.previous_strands:
                    new_strand.color = self.previous_strands[hash(tuple(new_strand))]

            self.strands.append(new_strands[0])
            self.strands.append(new_strands[1])

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
            max(x_coords) - min(x_coords), max(z_coords) - min(z_coords)
        )
