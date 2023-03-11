import logging

from PyQt6.QtCore import pyqtSignal

from structures.profiles import NucleicAcidProfile
from ui.config.tabs.domains.tables.base import DomainsBaseTable

logger = logging.getLogger(__name__)


class DomainsCountsTable(DomainsBaseTable):
    """Nucleic Acid Config Tab."""

    def __init__(self, parent) -> None:
        super().__init__(
            parent,
            ["Left Helix Counts", "Right Helix Counts"],
        )
