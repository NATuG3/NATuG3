import logging
from functools import partial
from typing import List, Tuple, Iterable, Literal

import pandas as pd
from PyQt6.QtCore import QTimer
from pandas import ExcelWriter

import settings
from structures.points import NEMid
from structures.profiles import NucleicAcidProfile
from structures.strands import utils
from structures.strands.strand import Strand
from utils import show_in_file_explorer

logger = logging.getLogger(__name__)


class Strands:
    """
    A container for multiple strands.

    Attributes:
        nucleic_acid_profile: The nucleic acid settings for the sequencing container.
        strands: The actual sequencing.
        up_strands: All up sequencing.
        down_strands: All down sequencing.
        name: The name of the strands object. Used when exporting the strands object.

    Methods:
        conjunct()
        up_strands(), down_strands()
        recompute(), recolor()
        append()
        remove()
        export()
    """

    def __init__(
        self,
        nucleic_acid_profile: NucleicAcidProfile,
        strands: Iterable[Strand],
        name: str = "Strands",
    ) -> None:
        """
        Initialize an instance of Strands.

        Args:
            nucleic_acid_profile: The nucleic acid settings for the sequencing container.
            strands: A list of sequencing to create a Strands object from.
            name: The name of the strands object. Used when exporting the strands object.
        """
        self.name = name
        self.nucleic_acid_profile = nucleic_acid_profile
        self.strands = list(strands)
        self.recompute()

    def __contains__(self, item):
        """Check if a strand or point is contained within this container."""
        if item in self.strands:
            return True
        else:
            for strand in self.strands:
                for item_ in strand:
                    if item_ is item:
                        return True

    def __len__(self):
        """Obtain the number of sequencing this Strands object contains."""
        return len(self.strands)

    def to_file(
        self, filepath: str, mode: Literal["xlsx"], open_in_file_explorer: bool = True
    ) -> None:
        """
        Export all sequences to a file.

        Data exported includes the following for each strand:
            - Strand name
            - Sequence
            - Sequence color

        Args:
            filepath: The filepath to export to. Do not include the file suffix.
            mode: The mode to export in.
            open_in_file_explorer: Whether to open the file location in file after exporting.
        """
        if "." in filepath:
            raise ValueError(
                "Filepath includes a suffix. Do not include suffixes in filepaths."
            )
        filepath = f"{filepath}.{mode}"

        if mode == "xlsx":
            # create a pandas dataset for exporting to the spreadsheet
            dataset = []
            for index, strand in enumerate(self.strands):
                # the three columns of the spreadsheet are name, sequence, and color
                name = f"Strand #{index}"
                sequence = "".join(map(str, strand.sequence)).replace("None", "")
                color = utils.rgb_to_hex(strand.color)
                dataset.append(
                    (
                        name,
                        sequence,
                        color,
                    )
                )

            # compile the dataset into pd.DataFrame
            sequences = pd.DataFrame(
                dataset, columns=["Name", "Sequence (5' to 3')", "Color"]
            )

            # create an Excel writer object
            writer = ExcelWriter(filepath, engine="openpyxl")

            # export the dataframe to an Excel sheet
            sequences.to_excel(writer, sheet_name=self.name, index=False)

            # adjust the widths of the various columns
            worksheet = writer.sheets[self.name]
            worksheet.column_dimensions["A"].width = 15
            worksheet.column_dimensions["B"].width = 50
            worksheet.column_dimensions["C"].width = 15
            worksheet.column_dimensions["D"].width = 15

            # Save the workbook
            workbook = writer.book
            workbook.save(filepath)

            # log
            logger.info("Exported sequences as excel @ {filepath}")
        else:
            # raise an error if the mode is invalid
            raise ValueError("Invalid export mode.", mode)

        if open_in_file_explorer:
            QTimer.singleShot(500, partial(show_in_file_explorer, filepath))
            logger.info(f"Opened export @ {filepath} in file explorer.")

    @property
    def up_strands(self):
        return list(filter(lambda strand: strand.down_strand, self.strands))

    @property
    def down_strands(self):
        return list(filter(lambda strand: strand.up_strand, self.strands))

    def recompute(self):
        """Reparent and recompute sequencing."""
        # reparent all the sequencing
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
        Recompute colors for all sequencing contained within.
        Prevents touching sequencing from sharing colors.
        """
        for strand in self.strands:
            if strand.auto_color:
                if strand.interdomain:
                    illegal_colors: List[Tuple[int, int, int]] = []

                    for potentially_touching in self.strands:
                        if strand.touching(potentially_touching):
                            illegal_colors.append(potentially_touching.color)

                    for color in settings.colors["sequencing"]["colors"]:
                        if color not in illegal_colors:
                            strand.color = color
                            break
                else:
                    if strand.up_strand:
                        strand.color = settings.colors["sequencing"]["greys"][1]
                    elif strand.down_strand:
                        strand.color = settings.colors["sequencing"]["greys"][0]
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
            - NEMid.matching may be changed based on whether the strand is closed or not.
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

        # new sequencing we are creating
        new_strands = [
            Strand(self.nucleic_acid_profile),
            Strand(self.nucleic_acid_profile),
        ]

        # log basic info for debugging
        logger.debug(
            f"NEMid1.strand {str(NEMid1.strand is NEMid2.strand).replace('True', 'is').replace('False', 'is not')}"
            f" NEMid2.strand"
        )
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
                # skip over all NEMids between NEMid 1's and NEMid 2's index
                # and crawl from NEMid 2 to the end of the strand
                new_strands[0].items.extend(strand.sliced(NEMid2.index, None))
                # crawl from one junction site to the other for the other strand
                new_strands[1].items.extend(strand.sliced(NEMid1.index, NEMid2.index))

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
            # remove the old sequencing
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

            # if both of the NEMids have closed sequencing
            elif NEMid1.strand.closed and NEMid2.strand.closed:
                # alternate sequencing that starts and ends at the junction site
                for NEMid_ in (NEMid1, NEMid2):
                    NEMid_.strand.items.rotate(len(NEMid_.strand) - 1 - NEMid_.index)

                # add the entire first reordered strand to the new strand
                new_strands[0].items.extend(NEMid1.strand.items)
                # add the entire second reordered strand to the new strand
                new_strands[0].items.extend(NEMid2.strand.items)

                new_strands[0].closed = True
                new_strands[1].closed = None

            # if neither of the NEMids have closed sequencing
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

        # recompute data for sequencing and append sequencing to master list
        for new_strand in new_strands:
            if not new_strand.empty:
                self.append(new_strand)

        # recompute the new sequencing
        [new_strand.recompute() for new_strand in new_strands]

        # if the new strand of NEMid#1 or NEMid#2 doesn't leave its domain
        # then mark NEMid1 as not-a-junction
        for NEMid_ in (NEMid1, NEMid2):
            if NEMid_.strand.interdomain:
                NEMid_.junction = True
            else:
                NEMid_.junction = False

        # assign the new juncmates
        NEMid1.juncmate = NEMid2
        NEMid2.juncmate = NEMid1

        self.recolor()
        self.recompute()

    @property
    def size(self) -> Tuple[float, float]:
        """
        Obtain the size of all sequencing when laid out.

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
