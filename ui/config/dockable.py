import logging
from typing import Dict

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDockWidget

import refs
from structures.domains import Domains
from structures.profiles import NucleicAcidProfile
from ui.config.panel import Panel

logger = logging.getLogger(__name__)


class Dockable(QDockWidget):
    def __init__(
        self, parent, profiles: Dict[str, NucleicAcidProfile], domains: Domains
    ):
        super().__init__(parent)

        # set titles/descriptions
        self.setObjectName("Config Dockable")
        self.setStatusTip("Config panel")
        self.setWindowTitle("Config")

        # Set window order
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)

        # store the actual link to the widget in self.config
        self.panel = Panel(self, profiles, domains)
        self.tab_area = self.panel.tab_area
        self.setWidget(self.panel)

        # Automatically move the dock widget to the left when it starts floating
        self.topLevelChanged.connect(self._on_top_level_changed)

    def _on_top_level_changed(self, floating: bool) -> None:
        """
        Worker function for when the dock widget becomes floating/docked.

        Args:
            floating (bool): Whether the dock widget is floating.
        """
        qr = self.frameGeometry()
        cp = refs.constructor.geometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
