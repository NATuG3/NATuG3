from typing import Tuple

from PyQt6.QtWidgets import QDockWidget

import refs
import ui.plotters
from workers.top_view import TopViewWorker


class Panel(QDockWidget):
    def __init__(self):
        super().__init__()

        self.setObjectName("Top View")
        self.setWindowTitle("Top View of Helices")
        self.setStatusTip("A plot of the top view of all domains")

        self.plot = ui.plotters.TopViewPlotter(
            TopViewWorker(refs.domains.current, refs.nucleic_acid.current),
            refs.domains.current,
            refs.nucleic_acid.current.D,
        )

        self.setWidget(self.plot)
        self.refresh()

    def refresh(self):
        """Update the current plot."""
        self.plot.worker = TopViewWorker(
            refs.domains.current, refs.nucleic_acid.current
        )
        self.plot.profile = refs.nucleic_acid.current
        self.plot.refresh()
        self.plot.point_clicked.connect(self.point_clicked)

    def point_clicked(self, point: Tuple[float, float]):
        """Signal for when a point in the plot is clicked."""
        # create the new active x-range for the plot
        range = self.plot.worker.u_coords.index(point[0])
        range = range - 1, range + 2

        # store the previous range of the ui
        previous = refs.constructor.side_view.plot.visibleRange()

        refs.constructor.side_view.plot.setXRange(*range)
        refs.constructor.side_view.plot.setYRange(-1, refs.strands.current.size[1] + 1)

        # if the new range is the same as the old range then this means
        # that the user has clicked on the button a second time and wants
        # to revert to the auto range of the side view plot
        if previous == refs.constructor.side_view.plot.visibleRange():
            refs.constructor.side_view.plot.autoRange()
