import dataclasses
import json
from dataclasses import dataclass
from typing import Type


@dataclass(kw_only=True)
class NucleicAcidProfile:
    """
    A container for all geometrical parameters for a nucleic acid.

    Attributes:
        D: Diameter of a domain.
        H: Height of a turn.
        g: Nucleoside-Mate Angle.
        T: There are T turns every B bases.
        B: There are B bases every T turns.
        Z_c: Characteristic height.
        Z_mate: Nucleoside-Mate Vertical Distance.
        theta_s: Switch angle.

    Methods:
        update: Update our nucleic_acid_profile in place.
        to_file: Write the nucleic acid nucleic_acid_profile to a file.
        write_worksheet: Write the NucleicAcidProfile to a tab in an Excel document.
    """

    D: float = 2.2
    H: float = 3.549
    g: float = 134.8
    T: int = 2
    B: int = 21
    Z_c: float = 0.17
    Z_mate: float = 0.094
    theta_s: float = 2.343

    @property
    def Z_b(self) -> float:
        """The base height."""
        return (self.T * self.H) / self.B

    @property
    def theta_b(self) -> float:
        """The base angle."""
        return 360 * (self.T / self.B)

    @property
    def theta_c(self) -> float:
        """The characteristic angle."""
        return 360 / self.B

    def update(self, profile: Type["NucleicAcidProfile"]) -> None:
        """
        Update our nucleic_acid_profile with theirs.

        Updates all of our attributes with the attributes of the given
        nucleic_acid_profile.

        This is useful for updating profiles in-place.
        """
        for attr in self.__dataclass_fields__:
            setattr(self, attr, getattr(profile, attr))

    def to_file(self, filepath: str) -> None:
        """
        Write the nucleic acid nucleic_acid_profile to a file.

        Args:
            filepath: The path to the file to write to.
        """
        with open(filepath, "w") as file:
            json.dump(dataclasses.asdict(self), file, indent=3)

    @classmethod
    def from_file(cls, filepath: str) -> "NucleicAcidProfile":
        """
        Load a NucleicAcidProfile from a file.

        Args:
            filepath: The path to the file to read from.
        """
        with open(filepath, "r") as file:
            return cls(**json.load(file))

    def write_worksheet(
        self, workbook, name="Nucleic Acid Profile", color="#FF6699"
    ) -> None:
        """
        Write the NucleicAcidProfile to a tab in an Excel document.

        Args:
            workbook (xlsxwriter.Workbook): The Excel document to write to.
            color: The color of the tab in the Excel document.
            name: The name of the tab in the Excel document.
        """
        sheet = workbook.add_worksheet(name)
        sheet.set_tab_color(color)

        subscript = workbook.add_format({"font_script": 2})
        comment_scale = {"x_scale": 1.5, "y_scale": 1.5}

        sheet.write("A1", "Name")
        sheet.write("B1", "Value")

        name = "D"
        value = self.D
        description = "The diameter of a given domain in nanometers"
        sheet.write("A1", name)
        sheet.write("B1", value)
        sheet.write_comment("A1", description, comment_scale)

        name = "H"
        value = self.H
        description = "The height of one turn of the helical axes in nanometers"
        sheet.write("A2", name)
        sheet.write("B2", value)
        sheet.write_comment("A2", description, comment_scale)

        name = "g"
        value = self.g
        description = (
            "The angle about the helical axis between a nucleoside and its "
            "Watson-Crick mate in degrees"
        )
        sheet.write("A3", name)
        sheet.write("B3", value)
        sheet.write_comment("A3", description, comment_scale)

        name = "T"
        value = self.T
        description = "There are T turns every B bases"
        sheet.write("A4", name)
        sheet.write("B4", value)
        sheet.write_comment("A4", description, comment_scale)

        name = "B"
        value = self.B
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
        value = self.Z_c
        description = "The height between two NEMids on a given helix"
        sheet.write_rich_string("A7", *name)
        sheet.write("B7", value)
        sheet.write_comment("A7", description, comment_scale)

        name = ("Z", subscript, "mate")
        value = self.Z_mate
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

    def __eq__(self, other: object) -> bool:
        """
        Whether our nucleic_acid_profile is the same as theirs.

        Checks all of our attributes against theirs.
        """
        if not isinstance(other, NucleicAcidProfile):
            return False

        return all(
            getattr(self, attr) == getattr(other, attr)
            for attr in dataclasses.asdict(self)
        )
