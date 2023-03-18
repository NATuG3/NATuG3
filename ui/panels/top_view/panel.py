from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QSlider,
    QVBoxLayout,
    QGroupBox,
)

import ui.plotters


class TopViewPanel(QGroupBox):
    """
    The main top view plot.

    The actual DNA/structural information is visually represented via the
    SideViewPlotter widget, which is NOT what this is. This widget is a container for
    that widget, and contains the refresh() method to update the plot based on the
    current program's settings. To access the child widget, use the .plot attribute.

    Attributes:
        plot (TopViewPlotter): The top view plot.

    Methods:
        refresh()
    """

    def __init__(self, parent, runner: "runner.Runner"):
        """
        Initialize the TopView plot.

        Args:
            parent: The main window.
            runner: NATuG's runner.
        """
        self.runner = runner
        super().__init__(parent)

        # Set the styles of the widget
        self.setObjectName("Top View")
        self.setTitle("Top View")
        self.setStatusTip("A plot of the top view of all domains")

        # Set the layout of the widget so that we can place the plot inside
        self.setLayout(QVBoxLayout())

        # Initialize the plot and connect the signals
        self.plot = ui.plotters.TopViewPlotter(
            domains=self.runner.managers.domains.current,
            domain_radius=self.runner.managers.nucleic_acid_profile.current.D,
            rotation=0,
        )
        self.plot.domain_clicked.connect(self._domain_clicked)
        self.layout().addWidget(self.plot)

        # set up rotation slider
        self.rotation_slider = QSlider(Qt.Orientation.Horizontal, parent=self)
        self.rotation_slider.valueChanged.connect(self.refresh)
        self.layout().addWidget(self.rotation_slider)

    def refresh(self):
        """
        Update the current plot.

        This updates the plot with the current domains, nucleic acid settings, and
        rotation.
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
        previous = self.runner.window.side_view.plot.visibleRange()

        # zoom in on the proper area of the plot
        self.runner.window.side_view.plot.setXRange(*range)
        self.runner.window.side_view.plot.setYRange(
            -1, self.runner.managers.strands.current.size[1] + 1
        )

        # if the new range is the same as the old range then this means
        # that the user has clicked on the button a second time and wants
        # to revert to the auto range of the side view plot
        if previous == self.runner.window.side_view.plot.visibleRange():
            self.runner.window.side_view.plot.autoRange()
