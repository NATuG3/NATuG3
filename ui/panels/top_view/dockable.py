from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDockWidget, QSlider, QWidget, QVBoxLayout

import refs
import ui.plotters


class Dockable(QDockWidget):
    """
    The top view panel.

    This panel contains a TopViewPlotter with the current domains being plotted and contains a useful refresh() method
    to update the plot with the most recent domains().

    Attributes:
        body (QWidget): The central body of the dockable. This is where all the widgets live.
        plot (TopViewPlotter): The top view plot.

    Methods:
        refresh()
    """

    def __init__(self, parent):
        """
        Initialize the TopView dockable area.

        Args:
            parent: The parent widget in which the top view dockable area is contained. Can be None.
        """
        super().__init__(parent)

        # set styles
        self.setObjectName("Top View")
        self.setWindowTitle("Top View of Helices")
        self.setStatusTip("A plot of the top view of all domains")

        # create the main body
        self.body = QWidget()
        self.body.setLayout(QVBoxLayout())

        # set up the plot
        self.plot = ui.plotters.TopViewPlotter(
            domains=refs.domains.current,
            domain_radius=refs.nucleic_acid.current.D,
            rotation=0,
        )

        self.plot.domain_clicked.connect(self._domain_clicked)
        self.body.layout().addWidget(self.plot)

        # set up rotation slider
        self.rotation_slider = QSlider(Qt.Orientation.Horizontal, parent=self)
        self.rotation_slider.valueChanged.connect(self.refresh)
        self.body.layout().addWidget(self.rotation_slider)

        # set body to be central widget
        self.setWidget(self.body)

        # perform initial refresh
        self.refresh()

    def refresh(self):
        """
        Update the current plot.

        This updates the plot with the current domains, nucleic acid settings, and rotation.
        """
        self.plot.rotation = (self.rotation_slider.value() * 360) / 99
        self.plot.refresh()
        self.plot.autoRange()

    def _domain_clicked(self, domain: int):
        """
        Slot for when a point in the plot is clicked.

        This method either zooms the side view in on the domain that was clicked,
        or restores the autofocus of the plot if the domain is already zoomed in on.

        Args:
            domain: The index of the domain that was clicked.
        """
        # create the new active x-range for the plot
        range = domain - 1, domain + 2

        # store the previous range of the ui
        previous = refs.constructor.side_view.plot.visibleRange()

        # zoom in on the proper area of the plot
        refs.constructor.side_view.plot.setXRange(*range)
        refs.constructor.side_view.plot.setYRange(-1, refs.strands.current.size[1] + 1)

        # if the new range is the same as the old range then this means
        # that the user has clicked on the button a second time and wants
        # to revert to the auto range of the side view plot
        if previous == refs.constructor.side_view.plot.visibleRange():
            refs.constructor.side_view.plot.autoRange()
