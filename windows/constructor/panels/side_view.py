from PyQt6.QtWidgets import QGroupBox, QVBoxLayout
from contextlib import suppress
import runner


class SideView(QGroupBox):
    def __init__(self):
        super().__init__()

        self.setObjectName("Side View")
        self.setLayout(QVBoxLayout())
        self.setTitle("Side View of Helices")
        self.setStatusTip("A plot of the side view of all domains")

        self.refresh()

    @property
    def plot(self):
        """The current plot."""
        return self.layout().itemAt(0)

    def refresh(self):
        """Update the current plot."""
        with suppress(TypeError):
            self.layout().removeWidget(self.plot)
        self.layout().addWidget(runner.plots.side_view.ui())
