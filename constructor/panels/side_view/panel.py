from PyQt6.QtWidgets import QGroupBox, QVBoxLayout

import references
from .action_menu import ActionMenu


class Panel(QGroupBox):
    def __init__(self):
        super().__init__()

        self.setObjectName("Side View")
        self.setLayout(QVBoxLayout())
        self.setTitle("Side View of Helices")
        self.setStatusTip("A plot of the side view of all domains")

        self.plot = references.plots.side_view.ui()

        self.layout().addWidget(self.plot)
        self.layout().addWidget(ActionMenu(self))

    def refresh(self):
        """Update the current plot."""
        self.plot.strands = references.strands
        self.plot.profile = references.nucleic_acid.current
        self.plot.refresh()
