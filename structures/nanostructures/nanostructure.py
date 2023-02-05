import logging

import xlsxwriter
from dataclasses import field, dataclass

from constants.directions import UP, DOWN
from runner import utils
from structures.domains import Domains
from structures.helices import DoubleHelices
from structures.points import NEMid, Nucleoside
from structures.points.point import Point, PointStyles
from structures.profiles import NucleicAcidProfile
from structures.strands import Strands

logger = logging.getLogger(__name__)


@dataclass
class Nanostructure:
    """
    An object representing an entire nanostructure.

    Attributes:
        strands: The strands in the nanostructure.
        helices: The helices in the nanostructure. Helices are strands that don't
            traverse multiple domains.
        domains: The domains in the nanostructure.
        nucleic_acid_profile: The nucleic acid settings that the nanostructure uses.
    """

    strands: field(default_factory=Strands)
    helices: field(default_factory=DoubleHelices)
    domains: field(default_factory=Domains)
    nucleic_acid_profile: field(default_factory=NucleicAcidProfile)

    def to_file(self, filepath: str) -> None:
        """
        Create a multipage spreadsheet with the current nanostructure.

        Args:
            filepath: The path to the file to save.

        Sheet 1: Nucleic Acid Profile
        Sheet 2: Domains
        Sheet 3: Strands
        Sheet 4: Helices
        """
        logger.debug("Saving nanostructure to file: %s", filepath)

        workbook = xlsxwriter.Workbook(filepath)

        def write_nucleic_acid_profile(sheet):
            subscript = workbook.add_format({"font_script": 2})

            sheet.write("A1", "Name")
            sheet.write("B1", "Value")

            comment_scale = {"x_scale": 1.5, "y_scale": 1.5}

            name = "D"
            value = self.nucleic_acid_profile.D
            description = "The diameter of a given domain in nanometers"
            sheet.write("A1", name)
            sheet.write("B1", value)
            sheet.write_comment("A1", description, comment_scale)

            name = "H"
            value = self.nucleic_acid_profile.H
            description = "The height of one turn of the helical axes in nanometers"
            sheet.write("A2", name)
            sheet.write("B2", value)
            sheet.write_comment("A2", description, comment_scale)

            name = "g"
            value = self.nucleic_acid_profile.g
            description = (
                "The angle about the helical axis between a nucleoside and its "
                "Watson-Crick mate in degrees"
            )
            sheet.write("A3", name)
            sheet.write("B3", value)
            sheet.write_comment("A3", description, comment_scale)

            name = "T"
            value = self.nucleic_acid_profile.T
            description = "There are T turns every B bases"
            sheet.write("A4", name)
            sheet.write("B4", value)
            sheet.write_comment("A4", description, comment_scale)

            name = "B"
            value = self.nucleic_acid_profile.B
            description = "There are T turns every B bases"
            sheet.write("A5", name)
            sheet.write("B5", value)
            sheet.write_comment("A5", description, comment_scale)

            name = ("Z", subscript, "b")
            value = "=(B4*B2)/B5"
            description = "The height between two NEMids on a given helix"
            sheet.write_rich_string("A6", *name)
            sheet.write("B6", value, None, "")
            sheet.write_comment("A6", description, comment_scale)

            name = ("Z", subscript, "c")
            value = self.nucleic_acid_profile.Z_c
            description = "The height between two NEMids on a given helix"
            sheet.write_rich_string("A7", *name)
            sheet.write("B7", value)
            sheet.write_comment("A7", description, comment_scale)

            name = ("Z", subscript, "mate")
            value = self.nucleic_acid_profile.Z_mate
            description = (
                "Vertical distance between a NEMid and its mate on the other helix"
            )
            sheet.write_rich_string("A8", *name)
            sheet.write("B8", value)
            sheet.write_comment("A8", description, comment_scale)

            name = ("θ", subscript, "c")
            value = "=360/B5"
            description = (
                "The smallest angle about the helical axis possible between two NEMids "
                "on the same helix."
            )
            sheet.write_rich_string("A9", *name)
            sheet.write("B9", value, None, "")
            sheet.write_comment("A9", description, comment_scale)

            name = ("θ", subscript, "b")
            value = "=360*(B4/B5)"
            description = "The angle about the helical axis between two NEMids"
            sheet.write_rich_string("A10", *name)
            sheet.write("B10", value, None, "")
            sheet.write_comment("A10", description, comment_scale)

        def write_domains_sheet(sheet):
            sheet.write(0, 0, "#")
            sheet.write(0, 1, "m")
            sheet.write(0, 2, "Left Helix Joints")
            sheet.write(0, 3, "Right Helix Joints")
            sheet.write(0, 4, "Left Helix Count (bottom)")
            sheet.write(0, 5, "Left Helix Count (initial)")
            sheet.write(0, 6, "Left Helix Count (top)")
            sheet.write(0, 7, "Other Helix Count (bottom)")
            sheet.write(0, 8, "Other Helix Count (initial)")
            sheet.write(0, 9, "Other Helix Count (top)")

            for i, domain in enumerate(self.domains.domains()):
                i += 1
                sheet.write(i, 0, domain.index + 1)  # domain.index is index-0
                sheet.write(i, 1, domain.theta_m_multiple)
                sheet.write(i, 2, "UP" if domain.left_helix_joint == UP else "DOWN")
                sheet.write(i, 3, "UP" if domain.right_helix_joint == UP else "DOWN")
                sheet.write(i, 4, domain.left_helix_count[0])
                sheet.write(i, 5, domain.left_helix_count[1])
                sheet.write(i, 6, domain.left_helix_count[2])
                sheet.write(i, 7, domain.other_helix_count[0])
                sheet.write(i, 8, domain.other_helix_count[1])
                sheet.write(i, 9, domain.other_helix_count[2])

            sheet.write(0, 9, "Symmetry")
            sheet.write(1, 9, self.domains.symmetry)

            sheet.write(0, 10, "Antiparallel")
            sheet.write(1, 10, self.domains.antiparallel)

        def write_strands_sheet(sheet):
            pass

        def write_helices_sheet(sheet):
            pass

        def write_points_sheet(sheet):
            border_color = "808080"

            category = workbook.add_format(
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
            column = workbook.add_format(
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

            sheet.set_column("A:A", 15)
            sheet.set_column("B:B", 12)
            sheet.merge_range("A1:B1", "ID", category)
            sheet.write("A2", "ID", column)
            sheet.write("B2", "Type", column)

            sheet.merge_range("C1:F1", "Data", category)
            sheet.write("C2", "X coord", column)
            sheet.write("D2", "Z coord", column)
            sheet.write("E2", "Angle", column)
            sheet.write("F2", "Direction", column)

            sheet.merge_range("G1:I1", "NEMid", category)
            sheet.write("G2", "Junctable", column)
            sheet.write("H2", "Juncmate", column)
            sheet.write("I2", "Junction", column)

            sheet.set_column("J:J", 12)
            sheet.write("J1", "Nucleoside", category)
            sheet.write("J2", "Base", column)

            sheet.set_column("K:K", 15)
            sheet.set_column("M:M", 10)
            sheet.merge_range("K1:M1", "Containers", category)
            sheet.write("K2", "Strand", column)
            sheet.write("L2", "Linkage", column)
            sheet.write("M2", "Domain", column)

            sheet.set_column("O:O", 6)
            sheet.set_column("P:P", 6)
            sheet.merge_range("N1:T1", "Styles", category)
            sheet.write("N2", "State", column)
            sheet.write("O2", "Symbol", column)
            sheet.write("P2", "Size", column)
            sheet.write("Q2", "Rotation", column)
            sheet.write("R2", "Fill Color", column)
            sheet.write("S2", "Outline Color", column)
            sheet.write("T2", "Outline Width", column)

            points = []
            for strand in self.strands:
                points.extend(strand.items.by_type(Point))

            for row, point in enumerate(points, start=3):
                # Store general point data
                sheet.write(f"A{row}", str(id(point)))
                # Column B is reserved for the type, which is written later
                sheet.write(f"C{row}", point.x_coord)
                sheet.write(f"D{row}", point.z_coord)
                sheet.write(f"E{row}", point.angle)
                sheet.write(f"F{row}", "UP" if point.direction == UP else "DOWN")

                # Store NEMid specific data
                if isinstance(point, NEMid):
                    sheet.write(f"B{row}", "NEMid")
                    sheet.write(f"G{row}", point.junctable)
                    sheet.write(f"H{row}", str(id(point.juncmate)))
                    sheet.write(f"I{row}", point.junction)

                # Store Nucleoside specific data
                if isinstance(point, Nucleoside):
                    sheet.write(f"B{row}", "Nucleoside")
                    sheet.write(f"J{row}", point.base)

                # Store the various containers that the point is in
                sheet.write(
                    f"K{row}",
                    f"Strand#{point.strand.strands.index(point.strand)}",
                )
                sheet.write(f"L{row}", str(id(point.linkage)))
                sheet.write(f"M{row}", f"Domain" f"#{point.domain.index}")

                # Store the point styles
                sheet.write(f"N{row}", point.styles.state)
                sheet.write(f"O{row}", point.styles.symbol)
                sheet.write(f"P{row}", point.styles.size)
                sheet.write(f"Q{row}", point.styles.rotation)
                sheet.write(f"R{row}", utils.rgb_to_hex(point.styles.fill))
                sheet.write(f"S{row}", utils.rgb_to_hex(point.styles.outline[0]))
                sheet.write(f"T{row}", point.styles.outline[1])

        nucleic_acid_profile_sheet = workbook.add_worksheet("Nucleic Acid Profile")
        nucleic_acid_profile_sheet.set_tab_color("#FF6699")
        write_nucleic_acid_profile(nucleic_acid_profile_sheet)

        domains_sheet = workbook.add_worksheet("Domains")
        domains_sheet.set_tab_color(r"#33CCCC")
        write_domains_sheet(domains_sheet)

        strands_sheet = workbook.add_worksheet("Strands")
        strands_sheet.set_tab_color(r"#FFCC00")
        write_strands_sheet(strands_sheet)

        points_sheet = workbook.add_worksheet("Points")
        points_sheet.set_tab_color(r"#669933")
        write_points_sheet(points_sheet)

        helices_sheet = workbook.add_worksheet("Helices")
        helices_sheet.set_tab_color(r"#99CCFF")
        write_helices_sheet(helices_sheet)

        workbook.close()

        logger.debug("Saved nanostructure")

    def from_file(self, filepath: str) -> None:
        pass
