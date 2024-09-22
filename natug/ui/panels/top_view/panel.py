from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtWidgets import QGroupBox, QSlider, QVBoxLayout

from natug import runner, utils
from natug.structures.domains import Domain
from natug.ui import plotters
from natug.ui.dialogs.refresh_confirmer.refresh_confirmer import \
    RefreshConfirmer


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
        self.setObjectName("topView")
        self.setStatusTip("A plot of the top view of all domains")

        # Set the layout of the widget so that we can place the plot inside
        self.setLayout(QVBoxLayout())

        # Initialize the plot and connect the signals
        self.plot = plotters.TopViewPlotter(
            domains=self.runner.managers.domains.current,
            circle_radius=self.runner.managers.nucleic_acid_profile.current.D,
            rotation=0,
        )
        self.plot.domain_clicked.connect(self._domain_clicked)
        self.plot.button_clicked.connect(self._button_clicked)
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

    @pyqtSlot(int)
    def _domain_clicked(self, domain: int):
        """
        Slot for when a point in the plot is clicked.

        This method either zooms the side view in on the domain that was clicked,
        or restores the autofocus of the plot if the domain is already zoomed in on.

        Args:
            domain: The index of the domain that was clicked.
        """

        if not self.runner.window.side_view.plot.auto_ranged():
            self.runner.window.side_view.plot.setRange(
                xRange=(domain - 1.5, domain + 0.5),
                yRange=(-0.5, self.runner.window.side_view.plot.height + 0.5),
            )
        else:
            # if the new range is the same as the old range then this means
            # that the user has clicked on the button a second time and wants
            # to revert to the auto range of the side view plot
            self.runner.window.side_view.plot.auto_range()

    def _button_clicked(self, domains: tuple[Domain]):
        """
        Slot for when a button in the plot is clicked.

        Inverts the two domains clicked.
        """

        if self.runner.managers.nucleic_acid_profile.current.B < 3:
            utils.warning(
                self,
                "Failure to invert",
                "Domains can only be inverted when the nucleic acid profile's B value is "
                "greater than 3. Please navigate to the nucleic acid tab of the config "
                "panel and update the value of B to allow for inversions.",
            )
            return
        if RefreshConfirmer.run(self.runner):
            self.runner.managers.domains.current.invert(*domains)
            self.runner.recompute()
            self.runner.snapshot()
