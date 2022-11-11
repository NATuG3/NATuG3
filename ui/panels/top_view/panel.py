from PyQt6.QtWidgets import QDockWidget

import refs
import ui
from workers.top_view import TopView


class Panel(QDockWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("Top View")
        self.setWindowTitle("Top View of Helices")
        self.setStatusTip("A plot of the top view of all domains")

        self.plot = ui.panels.top_view.Plotter()

        self.setWidget(self.plot)
        self.refresh()

    def refresh(self):
        """Update the current plot."""
        self.plot.worker = TopView(refs.domains.current, refs.nucleic_acid.current)
        self.plot.profile = refs.nucleic_acid.current
        self.plot.refresh()
