from PyQt6.QtWidgets import QDockWidget

from constructor.panels.top_view.worker import TopView
import references


class Panel(QDockWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("Top View")
        self.setWindowTitle("Top View of Helices")
        self.setStatusTip("A plot of the top view of all domains")

        self.plot = references.plots.top_view.ui()
        self.setWidget(self.plot)
        self.refresh()

    def refresh(self):
        """Update the current plot."""
        self.plot.worker = TopView(
            references.domains.current, references.nucleic_acid.current
        )
        self.plot.profile = references.nucleic_acid.current
        self.plot.refresh()
