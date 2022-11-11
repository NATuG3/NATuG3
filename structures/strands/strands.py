import logging
import math
from collections import namedtuple, deque
from contextlib import suppress
from math import dist
from typing import List, NamedTuple

import helpers
import settings
from structures.misc import Profile
from structures.points import NEMid
from structures.strands.strand import Strand

logger = logging.getLogger(__name__)


class Strands:
    def __init__(self, strands: List[Strand]) -> None:
        """
        Initialize an instance of Strands.

        Args:
            strands: A list of strands to create a Strands object from.
        """
        assert [isinstance(strand, Strand) for strand in strands]
        self.strands = strands

        # assign juncmates
        for strand in self.strands:
            for NEMid_ in strand.NEMids:
                for test_strand in self.strands:
                    for test_NEMid in test_strand.NEMids:
                        if dist(NEMid_.position(), test_NEMid.position()) < settings.junction_threshold:
                            NEMid_.juncmate = test_NEMid
                            test_NEMid.juncmate = NEMid_

    def recolor(self):
        """
        Recompute colors for all strands contained within.
        Prevents touching strands from sharing colors.
        """
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
                    raise ValueError(
                        "Strand should all be up/down if it is single-domain."
                    )

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

        # save the old strand references
        old_strands = (NEMid1.strand, NEMid2.strand)

        # flag the new NEMids as junctions
        NEMid1.junction, NEMid2.junction = True, True
        NEMid1.juncmate, NEMid2.juncmate = NEMid2, NEMid1

        # new strands we are creating
        new_strands = [Strand(), Strand()]

        # log basic info for debugging
        logger.debug(f"NEMid1.index={NEMid1.index}; NEMid2.index={NEMid2.index}")
        logger.debug(f"NEMid1.closed={NEMid1.strand.closed}; NEMid2.closed={NEMid2.strand.closed}")
        logger.debug(f"NEMid1-strand-length={len(NEMid1.strand)}; NEMid2-strand-length={len(NEMid2.strand)}")

        if NEMid1.strand is NEMid2.strand:
            # create shorthand for strand since they are the same
            strand: Strand = NEMid1.strand  # == NEMid2.strand

            # remove the old strand
            # note that NEMid1.strand IS NEMid2.strand
            self.strands.remove(strand)
            if strand.closed:
                # append NEMids to a new strand until we reach the junction site
                for NEMid_ in strand.NEMids:
                    # start out by appending to the first new strand
                    if not dist(NEMid_.position(), NEMid1.position()) < settings.junction_threshold:
                        new_strands[0].items.append(NEMid_)
                    else:
                        new_strands[0].items.append(NEMid_)
                        break

                # append all other NEMids to the other new strand
                for NEMid_ in strand.NEMids:
                    if NEMid_ not in new_strands[0]:
                        new_strands[1].items.append(NEMid_)

                new_strands[0].closed = True
                new_strands[1].closed = True

                logger.info("Created closed-strand same-strand junction.")

            elif not strand.closed:
                if NEMid2.index < NEMid1.index:
                    # crawl from the index of the right NEMid to the index of the left NEMid
                    new_strands[0].items.extend(strand.sliced(NEMid2.index, NEMid1.index))

                    # crawl from the beginning of the strand to the index of the right NEMid
                    new_strands[1].items.extend(strand.sliced(0, NEMid2.index))

                    # crawl from the index of the left NEMid to the end of the strand
                    new_strands[1].items.extend(strand.sliced(NEMid1.index, None))

                elif NEMid1.index < NEMid2.index:
                    # crawl from the index of the left NEMid to the index of the right NEMid
                    new_strands[0].items.extend(strand.sliced(NEMid1.index, NEMid2.index))

                    # crawl from the beginning of the strand to the index of the left NEMid
                    new_strands[1].items.extend(strand.sliced(None, NEMid1.index))

                    # crawl from the index of the right NEMid to the end of the strand
                    new_strands[1].items.extend(strand.sliced(NEMid2.index, None))

                # the first new strand will now be closed
                new_strands[0].closed = True

                logger.info("Created open-strand same-strand junction.")

        elif NEMid1.strand is not NEMid2.strand:
            # remove the old strands
            self.strands.remove(NEMid1.strand)
            self.strands.remove(NEMid2.strand)

            if NEMid1.strand.closed or NEMid2.strand.closed:
                if NEMid1.strand.closed:
                    closed_strand_NEMid: NEMid = NEMid1
                    open_strand_NEMid: NEMid = NEMid2
                elif NEMid2.strand.closed:
                    closed_strand_NEMid: NEMid = NEMid2
                    open_strand_NEMid: NEMid = NEMid1

                new_strands[0].items.extend(open_strand_NEMid.strand.sliced(0, open_strand_NEMid.index))
                new_strands[0].items.extend(closed_strand_NEMid.strand.sliced(closed_strand_NEMid.index, None))
                new_strands[0].items.extend(closed_strand_NEMid.strand.sliced(0, closed_strand_NEMid.index))
                new_strands[0].items.extend(open_strand_NEMid.strand.sliced(open_strand_NEMid.index, None))

            elif NEMid1.strand.closed and NEMid2.strand.closed:
                # alternate strands that starts and ends at the junction site
                for NEMid_ in (NEMid1, NEMid2):
                    NEMid_.strand.items.rotate(len(NEMid_.strand)-1-NEMid_.index)

                # add the entire first reordered strand to the new strand
                new_strands[0].items.extend(NEMid1.strand.items)
                # add the entire second reordered strand to the new strand
                new_strands[0].items.extend(NEMid2.strand.items)

                # this new strand is closed
                new_strands[0].closed = True

                logger.info("Created cross-strand junction for two closed NEMids.")

            elif (not NEMid1.strand.closed) and (not NEMid2.strand.closed):
                # crawl from beginning of NEMid#1's strand to the junction site
                new_strands[0].items.extend(NEMid1.strand.sliced(0, NEMid1.index))
                # crawl from the junction site on NEMid#2's strand to the end of the strand
                new_strands[0].items.extend(NEMid2.strand.sliced(NEMid2.index, None))

                # crawl from the beginning of NEMid#2's strand to the junction site
                new_strands[1].items.extend(NEMid2.strand.sliced(0, NEMid2.index))
                # crawl from the junction on NEMid #1's strand to the end of the strand
                new_strands[1].items.extend(NEMid1.strand.sliced(NEMid1.index, None))

                logger.info("Created cross-strand junction for two non-closed NEMids.")

        for new_strand in new_strands:
            new_strand.recompute()
            if not new_strand.empty:
                self.strands.append(new_strand)

        # if the new strand of NEMid#1 or NEMid#2 doesn't leave its domain
        # then mark NEMid1 as not-a-junction
        for NEMid_ in (NEMid1, NEMid2):
            if not NEMid_.strand.interdomain:
                NEMid_.junction = False

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
            for NEMid_ in strand.items:
                NEMid_: NEMid
                x_coords.append(NEMid_.x_coord)
                z_coords.append(NEMid_.z_coord)

        return namedtuple("Size", "width height")(
            max(x_coords) - min(x_coords), max(z_coords) - min(z_coords)
        )
