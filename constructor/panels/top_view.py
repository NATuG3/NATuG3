from PyQt6.QtWidgets import QDockWidget

import references


class TopView(QDockWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("Top View")
        self.setWindowTitle("Top View of Helices")
        self.setStatusTip("A plot of the top view of all domains")

        self.refresh()

    @property
    def plot(self):
        """The current plot."""
        return self.widget()

    def refresh(self):
        """Update the current plot."""
        self.setWidget(references.plots.top_view.ui())
