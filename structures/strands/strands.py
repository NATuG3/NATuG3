import logging
from math import dist
from typing import List, Tuple, Iterable

import settings
from structures.points import NEMid
from structures.profiles import NucleicAcidProfile
from structures.strands.strand import Strand

logger = logging.getLogger(__name__)


class Strands:
    """
    A container for multiple strands.

    Attributes:
        nucleic_acid_profile: The nucleic acid settings for the strands container.
        strands: The actual strands.
        up_strands: All up strands.
        down_strands: All down strands.
    """

    def __init__(
        self, nucleic_acid_profile: NucleicAcidProfile, strands: Iterable[Strand]
    ) -> None:
        """
        Initialize an instance of Strands.

        Args:
            nucleic_acid_profile: The nucleic acid settings for the strands container.
            strands: A list of strands to create a Strands object from.
        """
        self.nucleic_acid_profile = nucleic_acid_profile
        self.strands = list(strands)
        self.recompute()

    def __len__(self):
        """Obtain the number of strands this Strands object contains."""
        return len(self.strands)

    @property
    def up_strands(self):
        return list(filter(lambda strand: strand.down_strand, self.strands))

    @property
    def down_strands(self):
        return list(filter(lambda strand: strand.up_strand, self.strands))

    def recompute(self):
        """Reparent and recompute strands."""
        # reparent all the strands
        for strand in self.strands:
            strand.parent = self
            strand.recompute()

    def index(self, item: object) -> int:
        """Obtain the index of a given strand."""
        return self.strands.index(item)

    def append(self, strand: Strand):
        """Add a strand to the container."""
        if not isinstance(strand, Strand):
            raise TypeError("Cannot add non-strand to strand list.", strand)
        self.strands.append(strand)

    def remove(self, strand: Strand):
        """Remove a strand from the container."""
        self.strands.remove(strand)

    def recolor(self) -> None:
        """
        Recompute colors for all strands contained within.
        Prevents touching strands from sharing colors.
        """
        for strand in self.strands:
            if strand.auto_color:
                if strand.interdomain:
                    illegal_colors: List[Tuple[int, int, int]] = []

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

    def conjunct(self, NEMid1: NEMid, NEMid2: NEMid) -> None:
        """
        Add/remove a junction where NEMid1 and NEMid2 overlap.

        Args:
            NEMid1: One NEMid at the junction site.
            NEMid2: Another NEMid at the junction site.

        Raises:
            ValueError: NEMids are ineligible to be made into a junction.

        Notes:
            - The order of NEMid1 and NEMid2 is arbitrary.
            - NEMid.juncmate and NEMid.junction may be changed for NEMid1 and/or NEMid2.
        """
        # ensure that both NEMids are junctable
        if (not NEMid1.junctable) or (not NEMid2.junctable):
            raise ValueError(
                "NEMids are not close enough to create a junction.",
                NEMid1,
                NEMid2,
            )

        # ensure that NEMid1 is the lefter NEMid
        if NEMid1.x_coord > NEMid2.x_coord:
            NEMid1, NEMid2 = NEMid2, NEMid1

        # new strands we are creating
        new_strands = [
            Strand(self.nucleic_acid_profile),
            Strand(self.nucleic_acid_profile),
        ]

        # log basic info for debugging
        logger.debug(f"NEMid1.index={NEMid1.index}; NEMid2.index={NEMid2.index}")
        logger.debug(
            f"NEMid1.closed={NEMid1.strand.closed}; NEMid2.closed={NEMid2.strand.closed}"
        )
        logger.debug(
            f"NEMid1-strand-length={len(NEMid1.strand)}; NEMid2-strand-length={len(NEMid2.strand)}"
        )

        if NEMid1.strand is NEMid2.strand:
            # create shorthand for strand since they are the same
            strand: Strand = NEMid1.strand  # == NEMid2.strand
            # remove the old strand
            self.remove(strand)

            if strand.closed:
                # crawl from the beginning of the strand to the junction site
                new_strands[0].items.extend(strand.sliced(0, NEMid1.index))
                # ensure that the last NEMid is the lefter NEMid of the junction site
                new_strands[0].items.append(NEMid1)
                # append all other NEMids to the other new strand
                new_strands[1].items.extend(
                    [NEMid_ for NEMid_ in strand.items if NEMid_ not in new_strands[0]]
                )

                new_strands[0].closed = True
                new_strands[1].closed = True

            elif not strand.closed:
                # this is the creating a loop strand case
                if NEMid2.index < NEMid1.index:
                    # crawl from the index of the right NEMid to the index of the left NEMid
                    new_strands[0].items.extend(
                        strand.sliced(NEMid2.index, NEMid1.index)
                    )
                    # crawl from the beginning of the strand to the index of the right NEMid
                    new_strands[1].items.extend(strand.sliced(0, NEMid2.index))
                    # crawl from the index of the left NEMid to the end of the strand
                    new_strands[1].items.extend(strand.sliced(NEMid1.index, None))
                elif NEMid1.index < NEMid2.index:
                    # crawl from the index of the left NEMid to the index of the right NEMid
                    new_strands[0].items.extend(
                        strand.sliced(NEMid1.index, NEMid2.index)
                    )
                    # crawl from the beginning of the strand to the index of the left NEMid
                    new_strands[1].items.extend(strand.sliced(0, NEMid1.index))
                    # crawl from the index of the right NEMid to the end of the strand
                    new_strands[1].items.extend(strand.sliced(NEMid2.index, None))

                new_strands[0].closed = True
                new_strands[1].closed = False

        elif NEMid1.strand is not NEMid2.strand:
            # remove the old strands
            self.remove(NEMid1.strand)
            self.remove(NEMid2.strand)

            # if one of the NEMids has a closed strand:
            if (NEMid1.strand.closed, NEMid2.strand.closed).count(True) == 1:
                # create references for the stand that is closed/the strand that is open
                if NEMid1.strand.closed:
                    closed_strand_NEMid: NEMid = NEMid1
                    open_strand_NEMid: NEMid = NEMid2
                elif NEMid2.strand.closed:
                    closed_strand_NEMid: NEMid = NEMid2
                    open_strand_NEMid: NEMid = NEMid1

                # crawl from beginning of the open strand to the junction site NEMid of the open strand
                new_strands[0].items.extend(
                    open_strand_NEMid.strand.sliced(0, open_strand_NEMid.index)
                )
                # crawl from the junction site's closed strand NEMid to the end of the closed strand
                new_strands[0].items.extend(
                    closed_strand_NEMid.strand.sliced(closed_strand_NEMid.index, None)
                )
                # crawl from the beginning of the closed strand to the junction site of the closed strand
                new_strands[0].items.extend(
                    closed_strand_NEMid.strand.sliced(0, closed_strand_NEMid.index)
                )
                # crawl from the junction site of the open strand to the end of the open strand
                new_strands[0].items.extend(
                    open_strand_NEMid.strand.sliced(open_strand_NEMid.index, None)
                )

                new_strands[0].closed = False
                new_strands[1].closed = None

            # if both of the NEMids have closed strands
            elif NEMid1.strand.closed and NEMid2.strand.closed:
                # alternate strands that starts and ends at the junction site
                for NEMid_ in (NEMid1, NEMid2):
                    NEMid_.strand.items.rotate(len(NEMid_.strand) - 1 - NEMid_.index)

                # add the entire first reordered strand to the new strand
                new_strands[0].items.extend(NEMid1.strand.items)
                # add the entire second reordered strand to the new strand
                new_strands[0].items.extend(NEMid2.strand.items)

                new_strands[0].closed = True
                new_strands[1].closed = None

            # if neither of the NEMids have closed strands
            elif (not NEMid1.strand.closed) and (not NEMid2.strand.closed):
                # crawl from beginning of NEMid#1's strand to the junction site
                new_strands[0].items.extend(NEMid1.strand.sliced(0, NEMid1.index))
                # crawl from the junction site on NEMid#2's strand to the end of the strand
                new_strands[0].items.extend(NEMid2.strand.sliced(NEMid2.index, None))

                # crawl from the beginning of NEMid#2's strand to the junction site
                new_strands[1].items.extend(NEMid2.strand.sliced(0, NEMid2.index))
                # crawl from the junction on NEMid #1's strand to the end of the strand
                new_strands[1].items.extend(NEMid1.strand.sliced(NEMid1.index, None))

                new_strands[0].closed = False
                new_strands[1].closed = False

        # recompute data for strands and append strands to master list
        for new_strand in new_strands:
            if not new_strand.empty:
                self.append(new_strand)

        # recompute the new strands
        [new_strand.recompute() for new_strand in new_strands]

        # if the new strand of NEMid#1 or NEMid#2 doesn't leave its domain
        # then mark NEMid1 as not-a-junction
        for NEMid_ in (NEMid1, NEMid2):
            if NEMid_.strand.interdomain:
                NEMid_.junction = True
            else:
                NEMid_.junction = False

        NEMid1.juncmate = NEMid2
        NEMid2.juncmate = NEMid1

        self.recolor()
        self.recompute()

    @property
    def size(self) -> Tuple[float, float]:
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

        return max(x_coords) - min(x_coords), max(z_coords) - min(z_coords)
