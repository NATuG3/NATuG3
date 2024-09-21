import itertools
import logging
from collections import deque
from copy import copy, deepcopy
from functools import partial
from typing import Generator, Iterable, List, Literal, Tuple
from uuid import uuid1

import pandas as pd
from pandas import ExcelWriter
from PyQt6.QtCore import QTimer
from xlsxwriter import Workbook

from natug import settings
from natug.constants.directions import DOWN, UP
from natug.structures.points import NEMid
from natug.structures.points.nick import Nick
from natug.structures.points.point import Point
from natug.structures.profiles import NucleicAcidProfile
from natug.structures.strands.linkage import Linkage
from natug.structures.strands.strand import Strand, StrandItems
from natug.utils import rgb_to_hex, show_in_file_explorer

logger = logging.getLogger(__name__)


class Strands:
    """
    A container for multiple strands.

    Attributes:
        nucleic_acid_profile: The nucleic acid settings for the strands container.
        strands: The actual strands.
        up_strands: All up strands.
        down_strands: All down strands.
        nicks: All Nick objects within the strand. Automatically managed when nicking.
        name: The user set name of the strands object.
        size: The width and height of the domains when they are all laid next to one
            another.
        uuid: A unique identifier for the strands object. Automatically generated.

    Methods:
        update: Update the strands object in-place with another Strands object.
        items: Obtain a list of all points and linkages in the container.
        nick: Nick the strands at the given point (split the strand into two).
        unnick: Unnick the strands at the given nick (merge the two strands).
        export_sequence: Export the sequence of all the strands to a file.
        randomize_sequences: Randomize the sequences of all strands.
        clear_sequences: Clear the sequences of all strands.
        index: Obtain the index of a strand.
        append: Append a strand to the strands object.
        extend: Extend the strands object with a list of new Strands objects.
        remove: Remove a strand from the strands object.
        style: Recompute styles for all the strands and items within the strands.
        link: Create a linkage between two endpoint NEMids.
        unlink: Remove a linkage between two endpoint NEMids.
        conjunct: Create a cross-strand or same-strand junction between two NEMids.
        to_json: Convert the strands object to a JSON serializable dictionary.
        write_worksheets: Write all the strands and their items to an excel
            workbook's worksheet.
        cross_screen: Whether at least one strand is cross_screen. This is determined
            based on the cross_screen attribute of strands, which is automatically set
            by the SideViewPlotter, but can be set manually for strands.
    """

    def __init__(
        self,
        nucleic_acid_profile: NucleicAcidProfile,
        strands: Iterable[Strand],
        name: str = "Strands",
        uuid: str = None,
    ) -> None:
        """
        Initialize an instance of Strands.

        Args:
            nucleic_acid_profile: The nucleic acid settings for the strands container.
            strands: A list of strands to create a Strands object from.
            name: The name of the strands object. Used when exporting the strands object.
            uuid: A unique identifier for the strands object. Automatically generated,
                but can be provided.
        """
        # Store various attributes
        self.name = name
        self.uuid = uuid or str(uuid1())
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

    def cross_screen(self):
        """
        Whether at least one strand is cross_screen.

        Determine whether at least one strand's cross_screen attribute is True.

        Returns:
            bool: Whether at least one strand is cross screen.
        """
        for strand in self:
            if strand.cross_screen:
                return True
        return False

    def update(self, other: "Strands") -> None:
        """
        Update the strands object in place with the data of another Strands object.

        Args:
            other: The other strands object to update from.
        """
        # Update the nucleic acid profile
        self.nucleic_acid_profile = other.nucleic_acid_profile

        self.strands = other.strands
        for strand in self.strands:
            strand.strands = self

    def items(self, type_restriction=object) -> Generator:
        """
        Obtain a list of all points and linkages in the container.

        Args:
            type_restriction: The type of points to yield. Defaults to object,
                which includes all types of points. To only yield NEMids, use NEMid.
                To yield both NEMids and Nicks, but not Nucleosides/other types, use
                (NEMid, Nick), for example.

        Yields:
            All points in the container.
        """
        for strand in self.strands:
            for item in strand.items.by_type(type_restriction):
                yield item

    def nick(self, point: Point, style: bool = True) -> None:
        """
        Nick the strands at the given point (split the strand into two).

        Args:
            point: The point to create a nick at.
            style: Whether to recompute the styles of the container.

        Raises:
            ValueError: If the point's strands strand is not a strand of ours.
        """
        assert isinstance(point, Point), f"Point must be a Point object. Got: {point}"

        # Obtain the strand
        strand = point.strand

        # Check if the strand is in this container.
        if strand not in self.strands:
            raise ValueError(
                f"The point's strands is not a strand of ours. "
                f"Point: {point}, Strand: {strand}, Strands: {self.strands}"
            )

        # Create a nick object from the point
        nick = Nick(point, previously_closed_strand=strand.closed)
        self.nicks.append(nick)

        # Store the point's index
        point_index = point.index

        if strand.closed:
            # Open up the strand by removing the point and then flagging it as open.
            new_strand_items = StrandItems()
            new_strand_items.extend(strand.items[point_index + 1 :])
            new_strand_items.extend(strand.items[:point_index])
            strand.items = new_strand_items
            strand.closed = False
        else:
            # Split the strand into two strands and then remove the old singular strand.
            new_strand_template = copy(strand)
            new_strand_template.items = None

            # The items that are before the nick goes into one strand.
            new_strand_1 = deepcopy(new_strand_template)
            new_strand_1.items = StrandItems(strand.items[:point_index])

            # And the rest go into another strand.
            new_strand_2 = deepcopy(new_strand_template)
            new_strand_2.items = StrandItems(strand.items[point_index + 1 :])

            for new_strand in (new_strand_1, new_strand_2):
                for item in new_strand.items.by_type(Point):
                    item.styles = copy(item.styles)
                    item.styles.strand = new_strand
                    item.strand = new_strand

            self.append(new_strand_1)
            self.append(new_strand_2)
            self.remove(strand)

        point.strand = None

        # Change the NEMid in the helix to a nick
        point.helix.data.points[point.helical_index] = nick

        if style:
            self.style()

    def unnick(self, nick: "Nick", style: bool = True) -> None:
        """
        Recombine a strand and remove a nick.

        The attributes of the longer strand are preserved.

        Args:
            nick: The nick to remove.
            style: Whether to style the container after the unnick.

        Raises:
            IndexError: If the nick is not in the container.
        """
        # Obtain the original point that the nick is replacing.
        point = nick.original_item

        # Ensure the nick is in the container.
        if nick not in self.nicks:
            raise IndexError(f"Nick {nick} is not in this container.")

        assert (
            nick.previous_item().strand is nick.next_item().strand
            if nick.previous_item().strand.closed
            else True
        )

        # Assign references to the strands before and after the nick.
        previous_item_strand = nick.previous_item().strand
        next_item_strand = nick.next_item().strand

        # Add back the point that used to exist instead of the nick to the end of the
        # strand that comes before the nick
        previous_item_strand.append(nick.original_item)

        # If the strand before the location of the nick is the same as the strand
        # after the location of the nick then the strand is closed, and we must
        # update the flag.
        if nick.previous_item().strand is nick.next_item().strand:
            logger.debug("Performing nick reversal that results in a closed strand.")
            previous_item_strand.closed = True
        # Otherwise extend the strand that comes before the nick (after appending the
        # item that used to exist in place of the nick) the strand of the point that
        # comes after the nick).
        else:
            logger.debug("Performing nick reversal that results in a open strand.")
            nick.previous_item().strand.extend(next_item_strand.items)
            self.strands.remove(next_item_strand)

        # Remove the nick.
        self.nicks.remove(nick)

        # Replace the slot in the helix's points with the original point.
        point.helix.data.points[point.helical_index] = point

        if style:
            self.style()

    def do_many(
        self,
        action: Literal["nick", "unnick", "highlight", "conjunct"],
        first_point: Point,
        repeat_every: int,
        repeat_for: int,
        bidirectional: bool,
        items_to_run_on: Iterable,
    ) -> None:
        """
        Run an action on many points by surfing a given array or the point's strand.

        Args:
            action: The action to run on many points.
            first_point: The point to run an action on first and then surf from.
            repeat_every: The number of nucleosides between each action call.
            repeat_for: The number of steps of repeat_every to take.
            bidirectional: Whether to repeat the bulk action going in both directions,
                as opposed to only in the direction of the point starting at the point.
            items_to_run_on: The iterable of Points to run the action along.

        Raises:
            ValueError: If the point's strand is not a strand of ours, or the point does
                not have a strand assigned.
        """
        # Check if the strand is in this container.
        if (first_point.strand is None) and (first_point.strand not in self.strands):
            raise ValueError(
                f"The point's strand is not a strand of ours. "
                f"Point: {first_point}, Strand: {first_point.strand}"
            )

        # fmt: off
        if action == "nick":
            def worker(point):
                if isinstance(point, NEMid):
                    self.nick(point, style=False)
        elif action == "unnick":
            def worker(point):
                if isinstance(point, Nick):
                    self.unnick(point, style=False)
        elif action == "highlight":
            def worker(point):
                point.highlighted = True
        elif action == "conjunct":
            def worker(point):
                if isinstance(point, NEMid) and point.juncmate is not None:
                    self.conjunct(point, point.juncmate, style=False)
        else:
            raise ValueError(f"Unknown action: {action}")
        # fmt: on

        first_point_index = tuple(items_to_run_on).index(first_point)

        if repeat_for is None:
            end_at = len(items_to_run_on)
        else:
            end_at = first_point_index + repeat_for * repeat_every

        if bidirectional:
            logger.debug("Running action %s bidirectionally.", action)
            start_at = first_point_index - end_at

            # If the action is conjunct, we assume that the user only wants to make
            # junctions for NEMids that have the same x coord as the first point
            # starting at the first junctable point, or symmetrically (which is why
            # we check whether the start_at is less than 1).
            if start_at < 1:
                if action == "conjunct":
                    for index, item in enumerate(items_to_run_on):
                        if (
                            isinstance(item, NEMid)
                            and item.junctable
                            and round(item.x_coord) == round(first_point.x_coord)
                        ):
                            start_at = index
                            break
                else:
                    start_at = 1
        else:
            start_at = first_point_index

        logger.debug(
            "Running action %s, starting at item %s to item %s, every %s items.",
            action,
            start_at,
            end_at,
            repeat_every,
        )

        for item in itertools.islice(items_to_run_on, start_at, end_at, repeat_every):
            worker(item)

        self.style()

    def export_sequence(
        self, filepath: str, open_in_file_explorer: bool = True, mode="xlsx"
    ) -> None:
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
            mode: The file format to export to. Currently only supports "xlsx".
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
            color = rgb_to_hex(strand.styles.color.value)
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

        if mode == "xlsx":
            filepath += ".xlsx"

            # export the dataframe to an Excel worksheet
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
                logger.info(f"Opened export @ %s in file explorer.", filepath)
        else:
            raise ValueError(f"Unknown mode: %s", mode)

    def randomize_sequences(self, overwrite: bool = False):
        """
        Randomize the sequences for all strands.

        Args:
            overwrite: Whether to overwrite existing sequences.
        """
        for strand in self.strands:
            strand.randomize_sequence(overwrite)

    def clear_sequences(self):
        """
        Clear the sequences for all strands.
        """
        for strand in self.strands:
            strand.clear_sequence()

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
        Recompute colors for all strands contained within, and all items within the
        strands.

        Notes:
            - Prevents touching strands from sharing colors.
        """
        strand_colors = itertools.cycle(settings.colors["strands"]["colors"])

        for strand in self.strands:
            interdomain = strand.interdomain()

            # Change all the linkages in the strand to either be pink if the strand
            # is interdomain, or very dark grey if the strand is not interdomain.
            if interdomain:
                for item in strand.items.by_type(Linkage):
                    item.styles.color = settings.colors["linkages"]["color"]
            else:
                for item in strand.items.by_type(Linkage):
                    item.styles.color = settings.colors["linkages"]["grey"]

            if strand.styles.thickness.automatic:
                if interdomain:
                    strand.styles.thickness.value = 9.5
                else:
                    strand.styles.thickness.value = 2

            if strand.styles.color.automatic:
                if interdomain:
                    strand.styles.color.value = next(strand_colors)
                else:
                    if strand.up_strand():
                        strand.styles.color.value = settings.colors["strands"]["greys"][
                            1
                        ]
                    else:
                        strand.styles.color.value = settings.colors["strands"]["greys"][
                            0
                        ]

            # Set the styles of each point based off new strand styles
            for item in strand.items.by_type(Point):
                item.styles.change_state("default")
        logger.debug("Recomputed strand styles.")

    def link(self, NEMid1: NEMid, NEMid2: NEMid) -> Linkage:
        """
        Create a linkage between two endpoint NEMids.

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
        assert NEMid1.strand.strands == self and NEMid2.strand.strands == self, (
            "NEMids must be in this container. "
            f"(NEMid1 [{NEMid1}] Strands: {NEMid1.strand.strands}, "
            f"NEMid2 [{NEMid2}] Strands: {NEMid2.strand.strands})"
        )
        assert NEMid1.is_endpoint(True) and NEMid2.is_endpoint(
            True
        ), "NEMids must be at the endpoints of their strands."
        assert isinstance(NEMid1, NEMid) and isinstance(
            NEMid2, NEMid
        ), "The input points must be NEMids."

        # Force NEMid1 to be the upwards NEMid
        if NEMid1.strand.direction == DOWN:
            NEMid1, NEMid2 = NEMid2, NEMid1

        # If a closed linkage is being created then the strands are the same and we
        # only need to remove one of them
        self.remove(NEMid1.strand)
        if NEMid1.strand is not NEMid2.strand:
            self.remove(NEMid2.strand)

        # Determine the strand that begins with NEMid1 and the strand that begins with
        # NEMid2
        if NEMid1.is_tail(True):
            begin_point = NEMid1.strand[-1]
            end_point = NEMid2.strand[0]
        else:
            begin_point = NEMid2.strand[-1]
            end_point = NEMid1.strand[0]

        # We will preserve the styles of the longer strand, so determine which strand
        # is longer
        if len(NEMid1.strand) > len(NEMid2.strand):
            longer_strand = NEMid1.strand
        else:
            longer_strand = NEMid2.strand

        closed = begin_point.strand is end_point.strand
        new_strand = Strand(
            name=f"{longer_strand.name} (linked)",
            # The new strand is closed if the strands being linked are the same
            closed=closed,
            styles=deepcopy(longer_strand.styles),
            nucleic_acid_profile=self.nucleic_acid_profile,
            items=begin_point.strand.items,
            strands=self,
        )
        new_strand.styles.strand = new_strand

        # Create a linkage. The first coordinate is NEMid1.position(), and the second
        # coordinate is NEMid2.position().
        linkage = Linkage(
            coord_one=begin_point.position(),
            coord_two=end_point.position(),
            strand=new_strand,
            inflection=UP,
        )
        new_strand.append(linkage)
        if not closed:
            new_strand.items.extend(end_point.strand.items)
        for item in new_strand.items:
            item.strand = new_strand

        assert [
            item.strand == new_strand for item in new_strand
        ], "All items in the new strand must have the new strand as their parent."

        # Add the new strand to the container
        self.append(new_strand)

        # Restyle the strands
        self.style()

        # Return the linkage
        return linkage

    def unlink(self, linkage: Linkage) -> Tuple[Strand, Strand]:
        """
        Split the strand at the site of a given linkage.

        Args:
            linkage: The linkage to split the strand at.

        Returns:
            The two new strands that were created.
        """
        assert (
            linkage.strand.strands is self
        ), "Linkage is not in this Strands container."

        logger.debug(f"Unlinking %s in Strands object %s.", linkage, self.name)
        logger.debug(f"Linkage is at index %s.", linkage.strand.index(linkage))

        if linkage.strand.closed:
            linkage_index = linkage.strand.index(linkage)
            linkage.strand.closed = False
            linkage.strand.items = StrandItems(
                linkage.strand[0:linkage_index] + linkage.strand[linkage_index:-1]
            )
            to_return = (linkage.strand,)
        else:
            # Create a copy of the strand that has the same styles and nucleic acid
            # profile as the original strand. The new strands will have the same name,
            # but with "(1)" and "(2)" at the ends of the names since they are now two
            # distinct strands.
            new_strand_one = Strand(
                name=f"{self.name} (1)",
                # If the linkage was in a closed strand, breaking the linkage would make
                # the strand no longer closed.
                closed=linkage.strand.closed,
                styles=deepcopy(linkage.strand.styles),
                nucleic_acid_profile=self.nucleic_acid_profile,
                strands=self,
            )
            new_strand_one.styles.strand = new_strand_one
            new_strand_two = deepcopy(new_strand_one)
            new_strand_two.styles.strand = new_strand_two
            new_strand_two.name = f"{self.name} (2)"

            # Split up the strand items of the linkage, and do not include the linkage
            new_strand_one.extend(
                tuple(linkage.strand[: linkage.strand.index(linkage)]),
            )
            new_strand_two.extend(
                tuple(linkage.strand[linkage.strand.index(linkage) + 1 :]),
            )

            # Add the new strands to the container
            self.append(new_strand_one)
            self.append(new_strand_two)

            # Remove the old strand from the container
            self.remove(linkage.strand)

            # Store the two new strands that are to be returned
            to_return = (new_strand_one, new_strand_two)

        # Restyle the strands and return the new strand(s)
        self.style()
        return to_return

    def conjunct(
        self,
        NEMid1: NEMid,
        NEMid2: NEMid,
        skip_checks: bool = False,
        style: bool = True,
    ) -> None:
        """
        Create a cross-strand or same-strand junction between two NEMids.

        Args:
            NEMid1: One NEMid at the junction site.
            NEMid2: Another NEMid at the junction site.
            skip_checks: Whether to skip checks for whether the junction is valid.
            style: Whether to restyle the strands after the junction is made.

        Raises:
            ValueError: NEMids are ineligible to be made into a junction.

        Notes:
            - The order of NEMid1 and NEMid2 is arbitrary.
            - NEMid.juncmate and NEMid.junction may be changed for NEMid1 and/or NEMid2.
            - NEMid.matching may be changed based on whether the strand is closed or
                not.
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

        # ensure that NEMid1 is the lefter domain NEMid
        if NEMid1.domain.index > NEMid2.domain.index:
            NEMid1, NEMid2 = NEMid2, NEMid1

        NEMid1_index = NEMid1.index
        NEMid2_index = NEMid2.index

        # new strands we are creating
        new_strands = [
            Strand(nucleic_acid_profile=self.nucleic_acid_profile),
            Strand(nucleic_acid_profile=self.nucleic_acid_profile),
        ]

        # log basic info for debugging
        logger.debug(
            f"NEMid1.strand {str(NEMid1.strand is NEMid2.strand).replace('True', 'is').replace('False', 'is not')}"
            f" NEMid2.strand"
        )
        logger.debug(f"NEMid1_index=%s; NEMid2_index=%s", NEMid1_index, NEMid2_index)
        logger.debug(
            f"NEMid1.closed=%s; NEMid2.closed=%s",
            NEMid1.strand.closed,
            NEMid2.strand.closed,
        )
        logger.debug(
            f"NEMid1-strand-length=%s; NEMid2-strand-length=%s",
            len(NEMid1.strand),
            len(NEMid2.strand),
        )

        if NEMid1.strand is NEMid2.strand:
            # create shorthand for strand since they are the same
            strand: Strand = NEMid1.strand  # == NEMid2.strand
            # remove the old strand
            self.remove(strand)

            if strand.closed:
                if NEMid1_index < NEMid2_index:
                    first_NEMid_index = NEMid1_index
                    other_NEMid_index = NEMid2_index
                else:
                    first_NEMid_index = NEMid2_index
                    other_NEMid_index = NEMid1_index

                # crawl from the beginning of the strand to the junction site
                new_strands[0].items.extend(strand[first_NEMid_index:other_NEMid_index])
                # skip over all NEMids between NEMid 1's and NEMid 2's index
                # and crawl from NEMid 2 to the end of the strand
                new_strands[1].items.extend(strand[other_NEMid_index:])
                # crawl from one junction site to the other for the other strand
                new_strands[1].items.extend(strand[:first_NEMid_index])

                new_strands[0].closed = True
                new_strands[1].closed = True

            elif not strand.closed:
                # this is the creating a loop strand case
                if NEMid2_index < NEMid1_index:
                    # crawl from the index of the right NEMid to the index of the
                    # left NEMid
                    new_strands[0].items.extend(strand[NEMid2_index:NEMid1_index])
                    # crawl from the beginning of the strand to the index of the
                    # right NEMid
                    new_strands[1].items.extend(strand[0:NEMid2_index])
                    # crawl from the index of the left NEMid to the end of the strand
                    new_strands[1].items.extend(strand[NEMid1_index:])
                elif NEMid1_index < NEMid2_index:
                    # crawl from the index of the left NEMid to the index of the
                    # right NEMid
                    new_strands[0].items.extend(strand[NEMid1_index:NEMid2_index])
                    # crawl from the beginning of the strand to the index of the left
                    # NEMid
                    new_strands[1].items.extend(strand[0:NEMid1_index])
                    # crawl from the index of the right NEMid to the end of the strand
                    new_strands[1].items.extend(strand[NEMid2_index:])

                new_strands[0].closed = True
                new_strands[1].closed = False

        else:  # NEMid1.strand is not NEMid2.strand:
            # remove the old strands
            self.remove(NEMid1.strand)
            self.remove(NEMid2.strand)

            # if one of the NEMids has a closed strand:
            if NEMid1.strand.closed ^ NEMid2.strand.closed:
                # create references for the stand that is closed/the strand that is open
                if NEMid1.strand.closed:
                    closed_strand_NEMid: NEMid = NEMid1
                    open_strand_NEMid: NEMid = NEMid2
                elif NEMid2.strand.closed:
                    closed_strand_NEMid: NEMid = NEMid2
                    open_strand_NEMid: NEMid = NEMid1
                else:
                    raise ValueError(
                        "One of the strands should be closed for this case."
                    )

                # crawl from beginning of the open strand to the junction site NEMid
                # of the open strand
                new_strands[0].items.extend(
                    open_strand_NEMid.strand[0 : open_strand_NEMid.index]
                )
                # crawl from the junction site's closed strand NEMid to the end of
                # the closed strand
                new_strands[0].items.extend(
                    closed_strand_NEMid.strand[closed_strand_NEMid.index :]
                )
                # crawl from the beginning of the closed strand to the junction site
                # of the closed strand
                new_strands[0].items.extend(
                    closed_strand_NEMid.strand[0 : closed_strand_NEMid.index]
                )
                # crawl from the junction site of the open strand to the end of the
                # open strand
                new_strands[0].items.extend(
                    open_strand_NEMid.strand[open_strand_NEMid.index :]
                )

                new_strands[0].closed = False
                new_strands[1].closed = False

            # if both of the NEMids have closed sequencing
            elif NEMid1.strand.closed and NEMid2.strand.closed:
                # convert the strands to deques so that they can be rotated
                NEMid1_strand_items_deque = deque(NEMid1.strand.items)
                NEMid2_strand_items_deque = deque(NEMid2.strand.items)

                # rotate the strands so that they start and end at the junction site
                NEMid1_strand_items_deque.rotate(len(NEMid1.strand) - NEMid1_index)
                NEMid2_strand_items_deque.rotate(len(NEMid2.strand) - NEMid2_index)

                all_strand_items = NEMid1_strand_items_deque + NEMid2_strand_items_deque
                all_strand_items.rotate(1)

                # add the entire first reordered strand to the new strand
                new_strands[0].items = StrandItems(all_strand_items)

                new_strands[0].closed = True
                new_strands[1].closed = False

            # if both of the NEMids are open (and thus are both not closed)
            elif not any((NEMid1.strand.closed, NEMid2.strand.closed)):
                # crawl from the beginning of NEMid#1's strand to the junction site,
                # including the junction site
                new_strands[0].items.extend(NEMid1.strand[:NEMid1_index])
                # crawl from one NEMid after the junction site on NEMid#2's strand
                # to the end of the strand
                new_strands[0].items.extend(NEMid2.strand[NEMid2_index:])

                # crawl from the beginning of NEMid#2's strand to the junction site,
                # including the junction site
                new_strands[1].items.extend(NEMid2.strand[:NEMid2_index])
                # crawl from one NEMid after the junction site on NEMid#1's strand
                # to the end of the strand
                new_strands[1].items.extend(NEMid1.strand[NEMid1_index:])

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

        for NEMid_ in (NEMid1, NEMid2):
            for index, item in enumerate(NEMid_.strand):
                if (
                    isinstance(item, NEMid)
                    and item.junctable
                    and (
                        NEMid_.strand[(index - 1) % len(NEMid_.strand)].domain
                        != NEMid_.strand[(index + 1) % len(NEMid_.strand)].domain
                    )
                ):
                    item.junction = True
                else:
                    item.junction = False

        if style:
            self.style()

    def y_min(self) -> float:
        """The minimum z coordinate of the strands container."""
        return min([strand.y_min() for strand in self.strands])

    def y_max(self) -> float:
        """The maximum z coordinate of the strands container."""
        return max([strand.y_max() for strand in self.strands])

    def x_min(self) -> float:
        """The minimum x coordinate of the strands container."""
        return min([strand.x_min() for strand in self.strands])

    def x_max(self) -> float:
        """The maximum x coordinate of the strands container."""
        return max([strand.x_max() for strand in self.strands])

    def height(self):
        """Obtain the height of the strands container."""
        return self.y_max() - self.y_min()

    def width(self):
        """Obtain the width of the strands container."""
        return self.x_max() - self.x_min()

    def size(self) -> Tuple[float, float]:
        """
        Obtain the size of the strands container.

        Returns:
            Tuple[float, float]: (width, height)

        Notes:
            This is a convenience method that returns the width and height of the
                strands container. If you don't need both, it is more efficient to
                call the width() and height() methods directly.
        """
        return self.width(), self.height()

    def to_json(self) -> dict:
        """
        Convert the domain to a JSON serializable dictionary.

        All the strands and nicks are referenced by their uuids. The ordering of
        strands and nicks is preserved.

        Returns:
            dict: JSON serializable dictionary
        """
        return {
            "name": self.name,
            "uuid": self.uuid,
            "data:strands": [strand.uuid for strand in self],
            "data:nicks": [nick.uuid for nick in self.nicks],
        }

    def write_worksheets(
        self,
        workbook: Workbook,
        strand_sheet_name: str = "Strands",
        strand_sheet_color: str = "#FFCC00",
        point_sheet_name: str = "Points",
        point_sheet_color: str = "#00CC99",
    ):
        """
        Write two worksheets to an Excel spreadsheet containing the strands and all
        of the points and linakges within them.

        This method creates two sheets: a "Strands" sheet and a "Points" sheet.
        The Strands sheet contains information for all the strands, including a
        list of their items by id, styles and more. The Points sheet contains more
        detailed information about each point, including its coordinates, style,
        and more. The strands sheet's items that reference points by ID are linked
        to the points sheet.

        Args:
            workbook: The Excel workbook to create a tab for.
            strand_sheet_name: The name of the strand worksheet.
            strand_sheet_color: The color of the strand worksheet tab.
            point_sheet_name: The name of the point worksheet.
            point_sheet_color: The color of the point worksheet tab.
        """
        from natug.structures.points import NEMid, Nucleoside

        row_to_point = {}
        point_id_to_row = {}
        i = 2
        for strand in self.strands:
            for item in strand.items:
                if isinstance(item, Point):
                    points = (item,)
                elif isinstance(item, Linkage):
                    points = item.items
                for point in points:
                    i += 1
                    row_to_point[i] = point
                    point_id_to_row[id(point)] = i

        border_color = "808080"

        # Format for the very top headers
        primary_headers = workbook.add_format(
            {
                "align": "center",
                "bottom": 1,
                "left": 1,
                "right": 1,
                "bottom_color": border_color,
                "left_color": border_color,
                "right_color": border_color,
            }
        )

        # Format for the headers below the top headers
        secondary_headers = workbook.add_format(
            {
                "top": 1,
                "bottom": 1,
                "left": 1,
                "right": 1,
                "top_color": border_color,
                "bottom_color": border_color,
                "left_color": border_color,
                "right_color": border_color,
            }
        )

        # Format for URLs and hyperlinks
        links = workbook.add_format({"color": "blue", "underline": 1})

        def write_strands_sheet(sheet):
            column_start = 0  # the column where the current strand begins

            for i, strand in enumerate(self.strands):

                def c(index: int) -> int:
                    return column_start + index

                # Overall strand header
                sheet.merge_range(0, c(0), 0, c(6), f"Strand#{i+1}", primary_headers)

                # Secondary strand headers
                sheet.merge_range(1, c(0), 1, c(1), "#", secondary_headers)

                sheet.merge_range(1, c(2), 1, c(3), "Data", secondary_headers)

                sheet.merge_range(1, c(4), 1, c(6), "Styles", secondary_headers)

                # Territory strand headers
                sheet.write(2, c(0), "ID", secondary_headers)
                sheet.write(2, c(1), "Name", secondary_headers)
                sheet.set_column(c(2), c(2), 12)
                sheet.write(2, c(2), "Closed", secondary_headers)

                sheet.set_column(c(3), c(3), 25)
                sheet.write(2, c(3), "Sequence", secondary_headers)
                sheet.set_column(c(4), c(6), 10)
                sheet.write(2, c(4), "Color", secondary_headers)
                sheet.write(2, c(5), "Thickness", secondary_headers)
                sheet.write(2, c(6), "Highlighted", secondary_headers)

                # Overall strand data
                sheet.write(3, c(0), str(id(strand)))
                sheet.write(3, c(1), strand.name)
                sheet.write(3, c(2), strand.closed)

                sequence = ""
                for item in strand.sequence:
                    sequence += item if item is not None else "X"

                sheet.write(3, c(3), "".join(sequence))

                color = rgb_to_hex(strand.styles.color.value)
                if strand.styles.color.automatic:
                    sheet.write(3, c(4), f"auto, {color}")
                else:
                    sheet.write(3, c(4), rgb_to_hex(strand.styles.color.value))

                thickness = strand.styles.thickness.value
                if strand.styles.thickness.automatic:
                    sheet.write(3, c(5), f"auto, {thickness}")
                else:
                    sheet.write(3, c(5), thickness)

                sheet.write(3, c(6), strand.styles.highlighted)

                # Add the strand items header
                sheet.merge_range(4, c(0), 4, c(6), f"Items", primary_headers)

                # Add the strand items subheader
                sheet.write(5, c(0), f"ID", secondary_headers)
                sheet.write(5, c(1), f"Type", secondary_headers)
                sheet.write(5, c(2), f"Overview", secondary_headers)
                sheet.merge_range(
                    5, c(3), 5, c(6), f"Linkage Sequence", secondary_headers
                )

                for row, item in enumerate(strand.items, start=6):
                    try:
                        item_row = point_id_to_row[id(item)]
                    except KeyError:
                        item_row = None

                    sheet.write(row, c(0), str(item_row))
                    sheet.write(row, c(1), item.__class__.__name__)
                    overview = '="(" & {x} & ", " & {y} & ")"'
                    overview = overview.format(
                        x=f"ROUND(Points!C{item_row}, 3)",
                        y=f"ROUND(Points!D{item_row}, 3)",
                    )

                    if isinstance(item, Linkage):
                        str_sequence = ""
                        if item.sequence:
                            for base in item.sequence:
                                str_sequence += "X" if base is None else base
                        overview = f"{item.plot_points}"
                    else:
                        str_sequence = ""

                    sheet.write(row, c(2), overview)

                    sheet.merge_range(row, c(3), row, c(6), str_sequence)

                column_start += 8

        def write_points_sheet(sheet):
            sheet.merge_range("A1:B1", "#", primary_headers)
            sheet.set_column("A:A", 5)
            sheet.write("A2", "ID", secondary_headers)
            sheet.set_column("B:B", 10)
            sheet.write("B2", "Type", secondary_headers)

            sheet.merge_range("C1:F1", "Data", primary_headers)
            sheet.write("C2", "X coord", secondary_headers)
            sheet.write("D2", "Z coord", secondary_headers)
            sheet.write("E2", "Angle", secondary_headers)
            sheet.set_column("F:F", 5)
            sheet.write("F2", "Direction", secondary_headers)

            sheet.merge_range("G1:I1", "NEMid", primary_headers)
            sheet.set_column("G:G", 6)
            sheet.write("G2", "Junctable", secondary_headers)
            sheet.set_column("H:H", 10)
            sheet.write("H2", "Juncmate", secondary_headers)
            sheet.set_column("I:I", 6)
            sheet.write("I2", "Junction", secondary_headers)

            sheet.set_column("J:J", 12)
            sheet.write("J1", "Nucleoside", primary_headers)
            sheet.write("J2", "Base", secondary_headers)

            sheet.merge_range("K1:M1", "Containers", primary_headers)
            sheet.set_column("K:K", 10)
            sheet.write("K2", "Strand", secondary_headers)
            sheet.write("L2", "Linkage", secondary_headers)
            sheet.set_column("M:M", 10)
            sheet.write("M2", "Domain", secondary_headers)

            sheet.merge_range("N1:T1", "Styles", primary_headers)
            sheet.write("N2", "State", secondary_headers)
            sheet.set_column("O:O", 5)
            sheet.write("O2", "Symbol", secondary_headers)
            sheet.set_column("P:P", 5)
            sheet.write("P2", "Size", secondary_headers)
            sheet.write("Q2", "Rotation", secondary_headers)
            sheet.write("R2", "Fill Color", secondary_headers)
            sheet.set_column("S:S", 11)
            sheet.write("S2", "Outline Color", secondary_headers)
            sheet.set_column("T:T", 11)
            sheet.write("T2", "Outline Width", secondary_headers)

            points = []
            for strand in self.strands:
                points.extend(strand.items.by_type(Point))

            for row, point in enumerate(points, start=3):
                # Store general point data
                sheet.write(f"A{row}", point_id_to_row[id(point)])
                # Column B is reserved for the type, which is written later
                sheet.write(f"C{row}", point.x_coord)
                sheet.write(f"D{row}", point.z_coord)
                sheet.write(f"E{row}", point.angle)
                sheet.write(f"F{row}", "UP" if point.direction == UP else "DOWN")

                # Store NEMid specific data
                if isinstance(point, NEMid):
                    sheet.write(f"B{row}", "NEMid")
                    sheet.write(f"G{row}", point.junctable)
                    if point.juncmate is not None:
                        juncmate_row = point_id_to_row[id(point.juncmate)]
                        sheet.write(
                            f"H{row}",
                            f'=HYPERLINK("#A{juncmate_row}", "Point#{juncmate_row}")',
                            links,
                        )
                    sheet.write(f"I{row}", point.junction)

                # Store Nucleoside specific data
                if isinstance(point, Nucleoside):
                    sheet.write(f"B{row}", "Nucleoside")
                    sheet.write(f"J{row}", point.base)

                # Store the various containers that the point is in
                sheet.write(
                    f"K{row}",
                    f"Strand#{point.strand.strands.index(point.strand) + 1}",
                )
                sheet.write(f"L{row}", str(id(point.linkage)))
                sheet.write(f"M{row}", f"Domain#{point.domain.index+1}")

                # Store the point styles
                sheet.write(f"N{row}", point.styles.state)
                sheet.write(f"O{row}", point.styles.symbol)
                sheet.write(f"P{row}", point.styles.size)
                sheet.write(f"Q{row}", point.styles.rotation)
                sheet.write(f"R{row}", rgb_to_hex(point.styles.fill))
                sheet.write(f"S{row}", rgb_to_hex(point.styles.outline[0]))
                sheet.write(f"T{row}", point.styles.outline[1])

        # Create the strands sheet, set its color, and write the data
        strands_sheet = workbook.add_worksheet(strand_sheet_name)
        strands_sheet.set_tab_color(strand_sheet_color)
        write_strands_sheet(strands_sheet)

        # Create the points sheet, set its color, and write the data
        points_sheet = workbook.add_worksheet(point_sheet_name)
        points_sheet.set_tab_color(point_sheet_color)
        write_points_sheet(points_sheet)
