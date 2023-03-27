import logging
from functools import partial
from threading import Thread
from typing import List

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout

import ui.dialogs.informers
import ui.plotters
from constants.toolbar import *
from structures.points.point import Point
from structures.strands import Strand
from structures.strands.linkage import Linkage
from ui.dialogs.linkage_config.linkage_config import LinkageConfig
from ui.dialogs.strand_config.strand_config import StrandConfig
from ui.panels.side_view import workers

logger = logging.getLogger(__name__)


class SideViewPanel(QGroupBox):
    """
    The side view panel.

    The tube shape from a top view is visually represented via the TopViewPlotter
    widget, which is NOT what this is. This widget is a container for that widget, and
    contains the refresh() method to update the plot based on the current program's
    settings. To access the child widget, use the .plot attribute.

    Attributes:
        plot (TopViewPlotter): The top view plot.

    Methods:
        refresh()
    """

    def __init__(self, parent, runner: "runner.Runner") -> None:
        """
        Initialize the SideView plot.

        Args:
            parent: The main window.
            runner: NATuG's runner.
        """
        self.runner = runner
        super().__init__(parent)

        # Set the styles of the widget
        self.setObjectName("sideView")
        self.setStatusTip("A plot of the side view of all domains")

        # Set the layout of the widget so that we can place the plot inside
        self.setLayout(QVBoxLayout())

        # Initialize the plot and connect the signals
        self.plot = ui.plotters.SideViewPlotter(
            self.runner.managers.strands.current,
            self.runner.managers.domains.current,
            self.runner.managers.nucleic_acid_profile.current,
            self.runner.managers.misc.plot_types,
        )
        self.plot.points_clicked.connect(self._on_points_clicked)
        self.plot.strand_clicked.connect(self._on_strand_click)
        self.plot.linkage_clicked.connect(self._on_linkage_clicked)
        self.layout().addWidget(self.plot)

    def refresh(self) -> None:
        """
        Update the current plot.

        This will update the current plot with the most recent strands, domains,
        nucleic acid, and plot mode. Then the plot will be refreshed.
        """
        self.plot.strands = self.runner.managers.strands.current
        self.plot.nucleic_acid = self.runner.managers.nucleic_acid_profile.current
        self.plot.point_types = self.runner.managers.misc.plot_types
        self.plot.refresh()

    @pyqtSlot(object)
    def _on_linkage_clicked(self, linkage: Linkage) -> None:
        """
        Slot for when a linkage is clicked.

        Opens a linkage dialog for configuring the linkage.

        Args:
            linkage: The linkage that was clicked.
        """
        dialog = LinkageConfig(self.parent(), linkage)
        dialog.updated.connect(self.refresh)
        dialog.show()
        self.refresh()

        logger.info(f"A linkage was clicked.")

    @pyqtSlot(object)
    def _on_strand_click(self, strand: Strand) -> None:
        """
        Slot for when a strand is clicked.

        Creates a StrandConfig dialog for the strand that was clicked.

        Args:
            strand: The strand that was clicked.
        """
        dialog = StrandConfig(self.parent(), strand=strand)
        dialog.updated.connect(self.refresh)
        dialog.show()
        self.refresh()

        logger.info(f"Strand #{strand.strands.index(strand)} was clicked.")

    @pyqtSlot(object)
    def _on_points_clicked(self, points) -> None:
        """
        Slot for when a point in the plot is clicked.

        Utilizes a worker thread to handle the point click.

        Args:
            points: The points that were clicked.
        """
        strands = self.runner.managers.strands.current
        domains = self.runner.managers.domains.current
        parent = self
        refresh = self.runner.window.side_view.plot.refresh

        worker = partial(
            logger.info, "Point was clicked but no worker handled the click"
        )

        repeat = self.runner.window.toolbar.repeat.isChecked()

        if self.runner.managers.toolbar.current == INFORMER:
            worker = partial(
                workers.informer,
                parent,
                points,
                strands,
                domains,
                refresh,
            )
        elif self.runner.managers.toolbar.current == LINKER:
            worker = partial(
                workers.linker,
                points,
                strands,
                refresh,
                self.runner,
            )
        elif self.runner.managers.toolbar.current == JUNCTER:
            worker = partial(
                workers.juncter,
                points,
                strands,
                refresh,
                self.runner,
                repeat,
            )
        elif self.runner.managers.toolbar.current == NICKER:
            worker = partial(
                workers.nicker,
                points,
                strands,
                self.runner,
                refresh,
                repeat,
            )
        elif self.runner.managers.toolbar.current == HIGHLIGHTER:
            worker = partial(
                workers.highlighter,
                points,
                refresh,
                repeat,
            )

        thread = Thread(target=worker)
        thread.run()
