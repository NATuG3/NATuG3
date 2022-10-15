import logging
from types import SimpleNamespace

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QVBoxLayout

import config.domains
import config.main
import config.nucleic_acid
import storage
from resources import fetch_icon

logger = logging.getLogger(__name__)


class Panel(QWidget):
    """Config panel."""

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("config/panel.ui", self)

        # call setup functions
        self._styling()
        self._tabs()

    def _styling(self):
        """Set icons/stylesheets/other styles for config panel."""
        self.update_graphs.setIcon(fetch_icon("reload-outline"))

    def _tabs(self):
        """Set up all tabs for config panel."""
        logger.debug("Building config panel...")

        # container to store tabs in
        self.tabs = SimpleNamespace()

        # set the nucleic acid tab
        # store actual widget in the tabs container
        self.tabs.nucleic_acid = config.nucleic_acid.Panel(self)
        self.nucleic_acid_tab.setLayout(QVBoxLayout())
        self.nucleic_acid_tab.layout().addWidget(self.tabs.nucleic_acid)

        # set the domains tab
        # store actual widget in the tabs container
        self.tabs.domains = config.domains.Panel()
        self.domains_tab.setLayout(QVBoxLayout())
        self.domains_tab.layout().addWidget(self.tabs.domains)

        @self.update_graphs.clicked.connect
        def _():
            storage.windows.constructor.panels.top_view.setWidget(
                storage.plots.top_view.ui()
            )
            storage.windows.constructor.setCentralWidget(storage.plots.side_view.ui())
