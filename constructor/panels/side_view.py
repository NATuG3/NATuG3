from PyQt6.QtWidgets import QGroupBox, QVBoxLayout

import references


previous_bounding_box = None


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
        self.layout().removeItem(self.plot)
        self.layout().addWidget(references.plots.side_view.ui(restore_bound=True))
