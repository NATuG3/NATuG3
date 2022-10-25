import logging
from types import SimpleNamespace

from PyQt6 import uic
from PyQt6.QtCore import QTimer
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
        self.update_graphs.setIcon(fetch_icon("reload-outline"))
        self._tabs()

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

        def graph_updater():
            """Worker for auto plot updating."""
            runner.windows.constructor.top_view.refresh()
            runner.windows.constructor.side_view.refresh()

        self.update_graphs.clicked.connect(graph_updater)

        self.auto_update_graph.updating = False
        def auto_graph_updater():
            if self.auto_update_graph.isChecked():
                if not self.auto_update_graph.updating:
                    self.auto_update_graph.updating = True
                    timer = QTimer(runner.application)
                    timer.setInterval(300)
                    timer.setSingleShot(True)

                    @timer.timeout.connect
                    def _():
                        graph_updater()
                        self.auto_update_graph.updating = False

                    timer.start()

        self.tabs.domains.updated.connect(auto_graph_updater)
        self.tabs.nucleic_acid.updated.connect(auto_graph_updater)
