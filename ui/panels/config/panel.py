import logging
from time import time
from types import SimpleNamespace

from PyQt6 import uic
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMessageBox, QPushButton, QDialog

import refs
import settings
from ui.panels import domains, nucleic_acid
from ui.resources import fetch_icon

logger = logging.getLogger(__name__)


class Panel(QWidget):
    """Config panel."""

    def __init__(self, parent) -> None:
        super().__init__(parent)
        uic.loadUi("ui/panels/config/panel.ui", self)
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

        def warn_and_refresh(self):
            # determine if there are any strands that the user has made
            # (if there are not then we do not need to warn the user)
            for strand in refs.strands.current.strands:
                if strand.interdomain:
                    popup = QDialog(refs.constructor)
                    uic.loadUi("ui/panels/config/warn_and_refresh.ui", popup)

                    popup.location.setText(
                        f"NATuG3/saves/{round(time())}.{settings.extension}"
                    )

                    popup.show()
                    break
                    # refs.strands.recompute()
                    # refs.constructor.top_view.refresh()
                    # refs.constructor.side_view.refresh()
            return False

        self.update_graphs.clicked.connect(warn_and_refresh)

        self.auto_update_graph.updating = False

        def auto_graph_updater():
            for strand in refs.strands.current.strands:
                if strand.interdomain:
                    return
            if self.auto_update_graph.isChecked():
                if not self.auto_update_graph.updating:
                    self.auto_update_graph.updating = True
                    timer = QTimer(refs.application)
                    timer.setInterval(200)
                    timer.setSingleShot(True)

                    @timer.timeout.connect
                    def _():
                        logger.info("Auto updating...")
                        refs.strands.recompute()
                        refs.constructor.top_view.refresh()
                        refs.constructor.side_view.refresh()
                        self.auto_update_graph.updating = False

                    timer.start()

        self.tabs.domains.updated.connect(auto_graph_updater)
        self.tabs.nucleic_acid.updated.connect(auto_graph_updater)
