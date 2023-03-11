import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHeaderView

from structures.profiles import NucleicAcidProfile
from ui.config.tabs.domains.tables.base import DomainsBaseTable

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

    def _prettify(self):
        super()._prettify()

        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)

        self.setColumnWidth(0, 40)
        self.setColumnWidth(1, 40)
        self.setColumnWidth(2, 45)
        self.setColumnWidth(3, 45)
        # self.setColumnWidth(4, 60)
