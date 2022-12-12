import logging
from functools import partial
from threading import Thread
from typing import List

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout

import refs
import ui.dialogs.informers
import ui.plotters
from constants.toolbar import *
from structures.points.point import Point
from structures.strands import Strand
from ui.dialogs.strand_config.strand_config import StrandConfig
from ui.panels.side_view import workers

logger = logging.getLogger(__name__)


class Panel(QGroupBox):
    """
    The side view panel.

    This panel contains a SideViewPlotter with the current strands being plotted and contains a useful refresh()
    method to automatically update the plot with the most current strands.
    """

    def __init__(self, parent) -> None:
        """
        Initialize the SideView panel.

        Args:
            parent: The parent widget in which the side view panel is contained. Can be None.
        """
        super().__init__(parent)

        self.setObjectName("Side View")
        self.setLayout(QVBoxLayout())
        self.setTitle("Side View of Helices")
        self.setStatusTip("A plot of the side view of all domains")

        self.plot = ui.plotters.SideViewPlotter(
            refs.strands.current, refs.nucleic_acid.current, refs.plot_mode.current
        )
        self.plot.points_clicked.connect(self.points_clicked)
        self.plot.strand_clicked.connect(self.strand_clicked)
        self.layout().addWidget(self.plot)

    def refresh(self) -> None:
        """
        Update the current plot.

        This will update the current plot with the most recent strands, domains, nucleic acid, and plot mode. Then
        the plot will be refreshed.
        """
        self.plot.strands = refs.strands.current
        self.plot.nucleic_acid = refs.nucleic_acid.current
        self.plot.mode = refs.plot_mode.current
        self.plot.refresh()

    def strand_clicked(self, strand: Strand) -> None:
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

        logger.info(f"Strand #{strand.parent.index(strand)} was clicked.")

    def points_clicked(self, points: List[Point]) -> None:
        """
        Slot for when a point in the plot is clicked.

        Utilizes a worker thread to handle the point click.

        Args:
            points: The points that were clicked.
        """
        strands = refs.strands.current
        domains = refs.domains.current
        parent = self
        refresh = refs.constructor.side_view.plot.refresh

        worker = partial(
            logger.info, "Point was clicked but no worker handled the click"
        )
        if refs.toolbar.current == INFORMER:
            worker = partial(
                workers.informer, parent, points, strands, domains, refresh
            )
        elif refs.toolbar.current == JUNCTER:
            worker = partial(workers.juncter, points, strands, refresh)
        elif refs.toolbar.current == NICKER:
            worker = partial(workers.nicker, points, strands)
        thread = Thread(target=worker)
        thread.run()
