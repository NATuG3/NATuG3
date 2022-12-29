from PyQt6.QtWidgets import QMenu

import refs
import refs.saver
import utils
from ui.resources import fetch_icon


class View(QMenu):
    """
    The view section of the menu bar.

    This is a submenu of the menu bar that contains the following actions:
        - Config
        - Top View
        - Recolor Strands
    """

    def __init__(self, parent):
        """
        Initialize the view section of the menu bar.

        Args:
            parent: The parent of the view section of the menu bar.
        """
        super().__init__("&View", parent)

        self._config()
        self._top_view()
        self._recolor()

    def _config(self):
        """Show/hide the config based on whether it is already being shown or not.."""
        self.config = self.addAction("Config")
        self.config.setStatusTip("Display the config tab menu")
        self.config.setIcon(fetch_icon("eye-outline"))
        self.config.triggered.connect(
            lambda: utils.reverse_hidenness(refs.constructor.config)
        )

    def _top_view(self):
        """Show/hide the top view based on whether it is already being shown or not."""
        self.top_view = self.addAction("Helices Top View")
        self.top_view.setStatusTip("Display the helices top view graph")
        self.top_view.setIcon(fetch_icon("eye-outline"))
        self.top_view.triggered.connect(
            lambda: utils.reverse_hidenness(refs.constructor.top_view)
        )

    def _recolor(self):
        """Recompute colors for the currently plotted strands."""
        self.recolor = self.addAction("Recolor Strands")
        self.recolor.setStatusTip("Recompute colors for strands")
        self.recolor.setIcon(fetch_icon("color-palette-outline"))
        self.recolor.triggered.connect(refs.strands.current.style)
        self.recolor.triggered.connect(refs.constructor.side_view.refresh)
