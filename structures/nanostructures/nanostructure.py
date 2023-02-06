import logging
from dataclasses import field, dataclass

import xlsxwriter

from structures.domains import Domains
from structures.helices import DoubleHelices
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

        self.nucleic_acid_profile.write_worksheet(workbook)
        self.domains.write_worksheet(workbook)
        self.strands.write_worksheets(workbook)

        workbook.close()

        logger.debug("Saved nanostructure")

    def from_file(self, filepath: str) -> None:
        pass
