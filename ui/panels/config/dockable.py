import logging
from typing import Dict

from PyQt6.QtWidgets import QDockWidget

from structures.domains import Domains
from structures.misc import Profile
from ui.panels.config.panel import Panel

logger = logging.getLogger(__name__)


class Dockable(QDockWidget):
    def __init__(self, profiles: Dict[str, Profile], domains: Domains):
        super().__init__()

        # set titles/descriptions
        self.setObjectName("Config Panel")
        self.setStatusTip("Config panel")
        self.setWindowTitle("Config")

        # store the actual link to the widget in self.config
        self.panel = Panel(self, profiles, domains)
        self.tab_area = self.panel.tab_area
        self.setWidget(self.panel)
