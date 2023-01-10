import logging
from contextlib import suppress
from functools import partial
from typing import List, Tuple, Iterable

import pandas as pd
from PyQt6.QtCore import QTimer
from pandas import ExcelWriter

import settings
from constants.directions import DOWN
from structures.helices import DoubleHelices
from structures.points import NEMid, Nucleoside
from structures.points.nick import Nick
from structures.points.point import Point
from structures.profiles import NucleicAcidProfile
from structures.strands import utils
from structures.strands.linkage import Linkage
from structures.strands.strand import Strand
from utils import show_in_file_explorer

logger = logging.getLogger(__name__)


class Strands:
    """
    A container for multiple strands.

    Attributes:
        nucleic_acid_profile: The nucleic acid settings for the strands container.
        strands: The actual strands.
        up_strands: All up strands.
        down_strands: All down strands.
        nicks: All Nick objects.
        name: The name of the strands object. Used when exporting the strands object.
        double_helices(List[Tuple[Strand, Strand]]): A list of tuples of up and down strands
            from when the object is loaded with the from_package class method.

    Methods:
        randomize_sequences: Randomize the sequences for all strands.
        clear_sequences: Clear the sequences for all strands.
        conjunct: Create a cross-strand exchange (AKA a junction).
        connect: Bind two arbitrary NEMids together.
        disconnect: Unbind two arbitrary NEMids.
        nick: Nicks the strands at the given point (splits the strand into two).
        from_double_helices: Create a Strands object from a DoubleHelices object.
        assign_junctability: Assigns the junctability of all NEMids in all strands.
        up_strands, down_strands: Obtain all up or down strands.
        recompute, recolor: Recompute or recolor all strands.
        append: Append a strand to the container.
        extend: Append multiple strands to the container.
        remove: Remove a strand from the container.
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
            nucleic_acid_profile: The nucleic acid settings for the strands container.
            strands: A list of strands to create a Strands object from.
            name: The name of the strands object. Used when exporting the strands object.
        """
        # Store various attributes
        self.name = name
        self.nucleic_acid_profile = nucleic_acid_profile
        self.strands = list(strands)

        # Create various containers
        self.nicks = []

        # Assign the strands attribute of all strands to this object
        for strand in self.strands:
            strand.strands = self

        # If this class is initialized with a list of strands, then there are no double
        # helices to store
        self.double_helices = None

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
        """Obtain the number of strands this Strands object contains."""
        return len(self.strands)

    def __getitem__(self, item):
        """Obtain a strand by index."""
        return self.strands[item]

    def __setitem__(self, key, value):
        """Set a strand at a given index."""
        self.strands[key] = value

    def __delitem__(self, key):
        """Delete a strand by index."""
        del self.strands[key]

    def __iter__(self):
        """Iterate over all strands."""
        return iter(self.strands)

    def points(self) -> List[Point]:
        """Obtain a list of all points in the container."""
        return [point for strand in self.strands for point in strand]

    def nick(self, point: Point) -> None:
        """
        Nicks the strands at the given point (splits the strand into two).

        Args:
            point: The point to create a nick at.

        Raises:
            ValueError: If the point's strands strand is not a strand of ours.
        """
        # Obtain the strand
        strand = point.strand

        # Check if the strand is in this container.
        if strand not in self.strands:
            raise ValueError(
                f"The point's strands is not a strand of ours. "
                f"Point: {point}, Strand: {strand}, Strands: {self.strands}"
            )

        # Create a nick object from the point
        nick = Nick(point, point.strand[point.index - 1], point.strand[point.index + 1])
        self.nicks.append(nick)

        # Split the strand into two strands.
        new_strands = strand.split(point)
        nick.previous_item.strand = new_strands[0]
        nick.next_item.strand = new_strands[1]

        # Remove the old strand.
        self.remove(strand)

        # Parent the new strands
        for strand in new_strands:
            strand.strands = self

        # Add the two new strands
        self.extend(new_strands)

        self.style()

    def unnick(self, nick: "Nick"):
        """
        Recombine a strand and remove a nick.

        The attributes of the longer strand are preserved.

        Raises:
            IndexError: If the nick is not in the container.
        """
        # Ensure the nick is in the container.
        if nick not in self.nicks:
            raise IndexError(f"Nick {nick} is not in this container.")

        # Obtain the strands that are before and after the nick.
        strand1 = nick.previous_item.strand
        strand2 = nick.next_item.strand

        # Then build the new strand.
        new_strand = Strand(**strand1.__dict__)  # create a deep copy of strand1
        new_strand.append(nick.original_item)
        new_strand.extend(strand2)

        # Remove the two strands and add the new strand.
        with suppress(ValueError):
            self.remove(strand1)
        with suppress(ValueError):
            self.remove(strand2)
        self.append(new_strand)

        # Remove the nick.
        self.nicks.remove(nick)

    @classmethod
    def from_double_helices(
        cls,
        nucleic_acid_profile: NucleicAcidProfile,
        double_helices: DoubleHelices,
        name: str = "Strands",
    ):
        """
        Load a Strands object from a double_helices of up and down strands.

        This double_helices is saved under self.double_helices, and is used primarily
        for determining matching NEMids and Nucleosides.

        This method automatically stores the Strands object in self.double_helices,
        and unpacks the strands (helices) from each double helix into self.strands.

        Args:
            nucleic_acid_profile: The nucleic acid settings for the strands container.
            double_helices: The double_helices to load from. This is a DoubleHelices
                object.
            name: The name of the strands object. Used when exporting the strands
                object.
        """
        strands: List[Strand] = []
        for double_helix in double_helices:
            for helix in double_helix:
                strands.append(helix)

        strands: "Strands" = cls(nucleic_acid_profile, strands, name)
        strands.double_helices = double_helices
        strands.style()

        return strands

    def to_file(self, filepath: str, open_in_file_explorer: bool = True) -> None:
        """
        Export all sequences to a file.

        Data exported includes the following for each strand:
            - Strand name
            - Sequence
            - Sequence color

        Args:
            filepath: The filepath to export to. Do not include the file suffix.
            open_in_file_explorer: Whether to open the file location in file after
                exporting.
        """
        if "." in filepath:
            raise ValueError(
                "Filepath includes a suffix. Do not include suffixes in filepaths."
            )

        # create a pandas dataset for exporting to the spreadsheet
        dataset = []
        for index, strand in enumerate(self.strands):
            # the three columns of the spreadsheet are name, sequence, and color
            name = f"Strand #{index}"
            sequence = "".join(map(str, strand.sequence)).replace("None", "")
            color = utils.rgb_to_hex(strand.styles.color.value)
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

        if open_in_file_explorer:
            QTimer.singleShot(500, partial(show_in_file_explorer, filepath))
            logger.info(f"Opened export @ {filepath} in file explorer.")

    def randomize_sequences(self, overwrite: bool = False):
        """
        Randomize the sequences for all strands.

        Args:
            overwrite: Whether to overwrite existing sequences.
        """
        for strand in self.strands:
            strand.randomize_sequence(overwrite)

    def clear_sequences(self, overwrite: bool = False):
        """
        Clear the sequences for all strands.

        Args:
            overwrite: Whether to overwrite existing sequences.
        """
        for strand in self.strands:
            strand.clear_sequence(overwrite)

    @property
    def up_strands(self):
        return list(filter(lambda strand: strand.down_strand(), self.strands))

    @property
    def down_strands(self):
        return list(filter(lambda strand: strand.up_strand(), self.strands))

    def index(self, item: object) -> int:
        """Obtain the index of a given strand."""
        return self.strands.index(item)

    def append(self, strand: Strand):
        """Add a strand to the container."""
        strand.strands = self
        self.strands.append(strand)

    def extend(self, strands: List[Strand]):
        """Add multiple strands to the container."""
        for strand in strands:
            self.append(strand)

    def remove(self, strand: Strand):
        """Remove a strand from the container."""
        strand.strands = None
        self.strands.remove(strand)

    def style(self) -> None:
        """
        Recompute colors for all strands contained within.
        Prevents touching strands from sharing colors.

        Args:
            skip_checks: Whether to skip checks for strand direction consistency.
        """
        for strand in self.strands:
            if strand.styles.thickness.automatic:
                if strand.interdomain():
                    strand.styles.thickness.value = 9.5
                else:
                    strand.styles.thickness.value = 2
            if strand.styles.color.automatic:
                if strand.interdomain():
                    illegal_colors: List[Tuple[int, int, int]] = []

                    for potentially_touching in self.strands:
                        if strand.touching(potentially_touching):
                            illegal_colors.append(
                                potentially_touching.styles.color.value
                            )

                    for color in settings.colors["strands"]["colors"]:
                        if color not in illegal_colors:
                            strand.styles.color.value = color
                            break
                else:
                    if strand.up_strand():
                        strand.styles.color.value = settings.colors["strands"]["greys"][
                            1
                        ]
                    elif strand.down_strand():
                        strand.styles.color.value = settings.colors["strands"]["greys"][
                            0
                        ]
                    else:
                        strand.styles.color.value = settings.colors["strands"]["greys"][
                            0
                        ]

            # Set the styles of each point based off new strand styles
            for item in strand.items.by_type(Point):
                item.styles.change_state("default")

    def link(self, NEMid1: NEMid, NEMid2: NEMid) -> None:
        """
        Create a linkage between two end NEMids.

        This conjoins two different strands, and places a Linkage object in between
        the two strands. The two strands that are being conjoined will be deleted,
        and a new strand that contains all the items of those two strands and a
        linkage will be created and added to the container.

        Args:
            NEMid1: A NEMid at either the beginning or end of a strand.
            NEMid2: A different NEMid at either the beginning or end of a strand.

        Returns:
            The Linkage object that was created.

        Notes:
            - NEMids must be at opposite ends of strands.
            - NEMids must be of the same direction.
            - The NEMids' parent strands must be in this Strands container.
            - Properties of the longer strand are preserved (styles, etc.).
        """
        # Check that the NEMids are in the same Strands container
        if NEMid1.strand.strands != self or NEMid2.strand.strands != self:
            raise ValueError(
                "NEMids's strands' Strands container must be in the same. ("
                f"{NEMid1.strand.strands} != {NEMid2.strand.strands})"
            )

        # Check that the NEMids are at opposite ends of the strands
        for NEMid_ in (NEMid1, NEMid2):
            NEMid_index = NEMid_.strand.items.by_type(NEMid).index(NEMid_)
            if not (
                NEMid_index == 0
                or NEMid_index == len(NEMid_.strand.items.by_type(NEMid)) - 1
            ):
                raise ValueError(
                    "NEMids must be at opposite ends of strands to be linked."
                )

        # Ensure that the NEMids are of different direction
        if NEMid1.strand.direction == NEMid2.strand.direction:
            raise ValueError("NEMids must be of different direction to be linked.")

        # Force NEMid1 to be the upwards NEMid
        if NEMid1.strand.direction == DOWN:
            NEMid1, NEMid2 = NEMid2, NEMid1

        # Remove the old strands from the container
        self.remove(NEMid1.strand)
        self.remove(NEMid2.strand)

        # Determine the strand that begins with NEMid1 and the strand that begins with
        # NEMid2
        if NEMid1.strand.NEMids().index(NEMid1) == 0:
            begins_with_NEMid = NEMid1
            ends_with_NEMid = NEMid2
        else:
            begins_with_NEMid = NEMid2
            ends_with_NEMid = NEMid1

        # Attempt to surf forward one point, if that does not work then try surfing
        # backwards. We need nucleosides.
        if isinstance(ends_with_NEMid.surf_strand(1), Nucleoside):
            nucleoside1 = ends_with_NEMid.strand.items[-1]
        else:
            nucleoside1 = ends_with_NEMid.strand.items[0]

        # Attempt to surf forward one point, if that does not work then try surfing
        # backwards. We need nucleosides.
        if isinstance(begins_with_NEMid.surf_strand(-1), Nucleoside):
            nucleoside2 = begins_with_NEMid.strand.items[0]
        else:
            nucleoside2 = begins_with_NEMid.strand.items[-1]

        linkage = Linkage(
            items=(
                nucleoside1,
                nucleoside2,
            )
        )

        # Build the linkage. The linkage begins with the Nucleoside after the first
        # NEMid, then ends with the Nucleoside before the second NEMid.
        new_strand = Strand(nucleic_acid_profile=self.nucleic_acid_profile)
        new_strand.extend(tuple(ends_with_NEMid.strand.items))
        new_strand.append(linkage)
        new_strand.extend(tuple(begins_with_NEMid.strand.items))
        new_strand.remove(nucleoside1)
        new_strand.remove(nucleoside2)

        # Add the new strand to the container
        self.append(new_strand)

        for item in new_strand:
            item.strand = new_strand

        # Restyle the strands
        self.style()

        # Return the linkage
        return linkage

    def conjunct(self, NEMid1: NEMid, NEMid2: NEMid, skip_checks: bool = False) -> None:
        """
        Add/remove a junction where NEMid1 and NEMid2 overlap.

        Args:
            NEMid1: One NEMid at the junction site.
            NEMid2: Another NEMid at the junction site.
            skip_checks: Whether to skip checks for whether the junction is valid.

        Raises:
            ValueError: NEMids are ineligible to be made into a junction.

        Notes:
            - The order of NEMid1 and NEMid2 is arbitrary.
            - NEMid.juncmate and NEMid.junction may be changed for NEMid1 and/or NEMid2.
            - NEMid.matching may be changed based on whether the strand is closed or not.
        """
        if not skip_checks:
            # ensure that both NEMids are junctable
            if (not NEMid1.junctable) or (not NEMid2.junctable):
                raise ValueError(
                    "NEMids are not both junctable.",
                    NEMid1,
                    NEMid2,
                )
            assert isinstance(NEMid1, NEMid)
            assert isinstance(NEMid2, NEMid)

        # ensure that NEMid1 is the lefter NEMid
        if NEMid1.x_coord > NEMid2.x_coord:
            NEMid1, NEMid2 = NEMid2, NEMid1

        # new strands we are creating
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
                    # crawl from the index of the right NEMid to the index of the
                    # left NEMid
                    new_strands[0].items.extend(
                        strand.sliced(NEMid2.index, NEMid1.index)
                    )
                    # crawl from the beginning of the strand to the index of the
                    # right NEMid
                    new_strands[1].items.extend(strand.sliced(0, NEMid2.index))
                    # crawl from the index of the left NEMid to the end of the strand
                    new_strands[1].items.extend(strand.sliced(NEMid1.index, None))
                elif NEMid1.index < NEMid2.index:
                    # crawl from the index of the left NEMid to the index of the
                    # right NEMid
                    new_strands[0].items.extend(
                        strand.sliced(NEMid1.index, NEMid2.index)
                    )
                    # crawl from the beginning of the strand to the index of the left
                    # NEMid
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

                # crawl from beginning of the open strand to the junction site NEMid
                # of the open strand
                new_strands[0].items.extend(
                    open_strand_NEMid.strand.sliced(0, open_strand_NEMid.index)
                )
                # crawl from the junction site's closed strand NEMid to the end of
                # the closed strand
                new_strands[0].items.extend(
                    closed_strand_NEMid.strand.sliced(closed_strand_NEMid.index, None)
                )
                # crawl from the beginning of the closed strand to the junction site
                # of the closed strand
                new_strands[0].items.extend(
                    closed_strand_NEMid.strand.sliced(0, closed_strand_NEMid.index)
                )
                # crawl from the junction site of the open strand to the end of the
                # open strand
                new_strands[0].items.extend(
                    open_strand_NEMid.strand.sliced(open_strand_NEMid.index, None)
                )

                new_strands[0].closed = False
                new_strands[1].closed = False

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
                # crawl from the junction site on NEMid#2's strand to the end of the
                # strand
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

        # strands the items in the strands
        for new_strand in new_strands:
            for item in new_strand.items:
                item.strand = new_strand

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

        self.style()

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
            for item in strand.items.by_type(Point):
                if item.x_coord is not None:
                    x_coords.append(item.x_coord)
                if item.z_coord is not None:
                    z_coords.append(item.z_coord)

        return max(x_coords) - min(x_coords), max(z_coords) - min(z_coords)
