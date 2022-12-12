from types import SimpleNamespace

from PyQt6.QtWidgets import QMenu

import refs
import refs.saver
from ui.resources import fetch_icon


class View(QMenu):
    def __init__(self, parent):
        super().__init__("&View", parent)

        # container for actions
        self.actions = SimpleNamespace()

        self.actions.config = self.addAction("Config")
        self.actions.config.setStatusTip("Display the config tab menu")
        self.actions.config.setIcon(fetch_icon("eye-outline"))
        self.actions.config.triggered.connect(
            lambda: helpers.reverse_hidenness(refs.constructor.config)
        )

        self.actions.top_view = self.addAction("Helices Top View")
        self.actions.top_view.setStatusTip("Display the helices top view graph")
        self.actions.top_view.setIcon(fetch_icon("eye-outline"))
        self.actions.top_view.triggered.connect(
            lambda: helpers.reverse_hidenness(refs.constructor.top_view)
        )

        self.actions.recolor = self.addAction("Recolor Strands")
        self.actions.recolor.setStatusTip("Recompute colors for sequencing")
        self.actions.recolor.setIcon(fetch_icon("color-palette-outline"))
        self.actions.recolor.triggered.connect(refs.strands.current.recolor)
        self.actions.recolor.triggered.connect(refs.constructor.side_view.refresh)
