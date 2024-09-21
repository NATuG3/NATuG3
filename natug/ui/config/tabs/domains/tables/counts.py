import logging

from PyQt6.QtWidgets import QHeaderView

from natug.ui.config.tabs.domains.tables.base import DomainsBaseTable

logger = logging.getLogger(__name__)


class DomainsCountsTable(DomainsBaseTable):
    """Nucleic Acid Config Tab."""

    def __init__(self, parent) -> None:
        super().__init__(
            parent,
            ["Up Helix Counts", "Down Helix Counts"],
        )
