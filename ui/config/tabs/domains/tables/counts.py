import logging

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHeaderView

from structures.profiles import NucleicAcidProfile
from ui.config.tabs.domains.tables.base import DomainsBaseTable

logger = logging.getLogger(__name__)


class DomainsCountsTable(DomainsBaseTable):
    """Nucleic Acid Config Tab."""

    def __init__(self, parent) -> None:
        super().__init__(
            parent,
            ["Up Helix Counts", "Down Helix Counts"],
        )

    def _prettify(self):
        super()._prettify()

        # All columns are stretch sized
        for index, column in enumerate(range(self.columnCount())):
            self.horizontalHeader().setSectionResizeMode(
                index, QHeaderView.ResizeMode.Stretch
            )
