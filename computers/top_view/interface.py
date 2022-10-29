import logging

import pyqtgraph as pg

from datatypes.misc import Profile

logger = logging.getLogger(__name__)


class Plotter(pg.PlotWidget):

    domain_brush = pg.mkBrush(color=(90, 90, 90))

    def __init__(self, worker, profile: Profile):
        """
        Initialize plotter instance.

        Args:
            worker (SideView): The actual side view worker item.
        """
        super().__init__()
        self.profile = profile
        self.worker = worker
        self._plot()
        self.disableAutoRange()

    def refresh(self):
        self.clear()
        self._plot()

    def clear(self):
        self.getPlotItem().clear()

    def _plot(self):
        # create references plot
        self.plot(
            self.worker.u_coords,
            self.worker.v_coords,
            symbol="o",
            symbolSize=self.profile.D,
            symbolBrush=self.domain_brush,
            pxMode=False,
        )

        # increase the view box padding, since... our symbols are VERY large circles and pyqtgraph calculates padding
        # from the actual points, so the circles get cut off
        self.getViewBox().setDefaultPadding(padding=0.18)

        # prevent user from interacting with the graph
        self.getViewBox().setAspectLocked(lock=True, ratio=1)

        # set axis units
        self.setLabel("bottom", units="Nanometers")
        self.setLabel("left", units="Nanometers")
