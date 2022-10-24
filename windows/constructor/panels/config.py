import logging
from types import SimpleNamespace

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QDockWidget

import domains
import nucleic_acid
import runner
from resources import fetch_icon

logger = logging.getLogger(__name__)


class Config(QDockWidget):
    def __init__(self):
        super().__init__()

        # set titles/descriptions
        self.setObjectName("Config Panel")
        self.setStatusTip("Config panel")
        self.setWindowTitle("Config")

        # store the actual link to the widget in self.config
        self.panel = _Panel(self)
        self.setWidget(self.panel)


class _Panel(QWidget):
    """Config panel."""

    def __init__(self, parent) -> None:
        super().__init__(parent)
        uic.loadUi("windows/constructor/panels/config.ui", self)

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
        self.tabs.nucleic_acid = nucleic_acid.Panel(self)
        self.nucleic_acid_tab.setLayout(QVBoxLayout())
        self.nucleic_acid_tab.layout().addWidget(self.tabs.nucleic_acid)

        # set the domains tab
        # store actual widget in the tabs container
        self.tabs.domains = domains.Panel(self.parent())
        self.domains_tab.setLayout(QVBoxLayout())
        self.domains_tab.layout().addWidget(self.tabs.domains)

        @self.update_graphs.clicked.connect
        def _():
            # load and set new plot areas
            runner.windows.constructor.top_view.refresh()
            runner.windows.constructor.side_view.refresh()
