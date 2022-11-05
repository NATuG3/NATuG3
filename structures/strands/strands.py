import logging
from itertools import islice
from collections import namedtuple
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

    def recolor(self):
        for strand in self.strands:
            if strand.interdomain:
                illegal_colors = []

                for potentially_touching in self.strands:
                    if strand.touching(potentially_touching):
                        illegal_colors.append(potentially_touching.color)

                for color in settings.colors["strands"]["colors"]:
                    if color not in illegal_colors:
                        strand.color = color
                        break
            else:
                if strand.up_strand:
                    strand.color = settings.colors["strands"]["greys"][1]
                elif strand.down_strand:
                    strand.color = settings.colors["strands"]["greys"][0]
                else:
                    raise ValueError("Strand should all be up/down if it is single-domain.")


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

        # remove the old strands
        self.strands.remove(NEMid1.strand)
        self.strands.remove(NEMid2.strand)

        new_strands = [Strand([]), Strand([])]

        if NEMid1.strand is NEMid2.strand:
            # first new strand
            new_strands[0].extend(islice(NEMid1.strand, NEMid1.index(), NEMid2.index()+1))

            # second new strand
            new_strands[1].extend(islice(NEMid1.strand, 0, NEMid1.index() + 1))
            new_strands[1].extend(islice(NEMid1.strand, NEMid2.index(), None))

            logger.info("Created same-strand junction.")
        elif NEMid1.strand is not NEMid2.strand:
            # first new strand
            new_strands[0].extend(islice(NEMid1.strand, 0, NEMid1.index() + 1))
            new_strands[0].extend(islice(NEMid2.strand, NEMid2.index() + 1, None))

            # second new strand
            new_strands[1].extend(islice(NEMid2.strand, 0, NEMid2.index() + 1))
            new_strands[1].extend(islice(NEMid1.strand, NEMid1.index() + 1, None))

            logger.info("Created same-strand junction.")

        for new_strand in new_strands:
            new_strand.assign_strands()

        self.strands.append(new_strands[0])
        self.strands.append(new_strands[1])

        self.recolor()

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
