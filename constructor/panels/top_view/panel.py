from PyQt6.QtWidgets import QDockWidget

import references
from constructor.panels.top_view.worker import TopView
from references import constructor


class Panel(QDockWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("Top View")
        self.setWindowTitle("Top View of Helices")
        self.setStatusTip("A plot of the top view of all domains")

        self.plot = constructor.panels.top_view.Plotter()

        self.setWidget(self.plot)
        self.refresh()

    def refresh(self):
        """Update the current plot."""
        self.plot.worker = TopView(
            references.domains.current, references.nucleic_acid.current
        )
        self.plot.profile = references.nucleic_acid.current
        self.plot.refresh()
