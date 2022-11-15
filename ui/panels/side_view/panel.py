import logging

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout

import ui.panels.side_view

logger = logging.getLogger(__name__)


class Panel(QGroupBox):
    def __init__(self):
        super().__init__()

        self.setObjectName("Side View")
        self.setLayout(QVBoxLayout())
        self.setTitle("Side View of Helices")
        self.setStatusTip("A plot of the side view of all domains")

        self.plot = ui.panels.side_view.Plotter()
        self.layout().addWidget(self.plot)

    def refresh(self):
        """Update the current plot."""
        self.plot.refresh()
