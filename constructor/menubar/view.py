from types import SimpleNamespace

from PyQt6.QtWidgets import QMenu

import helpers
import references
import references.saver
from resources import fetch_icon


class View(QMenu):
    def __init__(self, parent):
        super().__init__("&View", parent)

        # container for actions
        self.actions = SimpleNamespace()

        # view -> "Config" -> hide/unhide
        config = self.actions.config = self.addAction("Config")
        config.setStatusTip("Display the config tab menu")
        # will be checked/unchecked based on if widget is shown
        config.setIcon(fetch_icon("eye-outline"))
        config.triggered.connect(
            lambda: helpers.reverse_hidenness(references.constructor.panels.config)
        )

        # view -> "top view" -> hide/unhide
        top_view = self.actions.top_view = self.addAction("Helices Top View")
        top_view.setStatusTip("Display the helices top view graph")
        # will be checked/unchecked based on if widget is shown
        top_view.setIcon(fetch_icon("eye-outline"))
        top_view.triggered.connect(
            lambda: helpers.reverse_hidenness(references.constructor.top_view)
        )
