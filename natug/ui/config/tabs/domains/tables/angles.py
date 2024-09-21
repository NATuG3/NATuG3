import logging

from PyQt6.QtWidgets import QHeaderView

from natug.structures.profiles import NucleicAcidProfile
from natug.ui.config.tabs.domains.tables.base import DomainsBaseTable

logger = logging.getLogger(__name__)


class DomainsAnglesTable(DomainsBaseTable):
    """Nucleic Acid Config Tab."""

    def __init__(self, parent, nucleic_acid_profile: NucleicAcidProfile) -> None:
        super().__init__(
            parent,
            ["L-Joint", "R-Joint", "s", "m", "θi"],
        )
        # Store the nucleic acid nucleic_acid_profile
        self.nucleic_acid_profile = nucleic_acid_profile
