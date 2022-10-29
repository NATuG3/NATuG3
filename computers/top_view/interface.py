import logging

import pyqtgraph as pg

from datatypes.misc import Profile

logger = logging.getLogger(__name__)
previous_bounding_box = None


class Plotter(pg.PlotWidget):

    domain_brush = pg.mkBrush(color=(90, 90, 90))

    def __init__(self, worker, profile: Profile, restore_bound: bool = False):
        """
        Initialize plotter instance.

        Args:
            worker (SideView): The actual side view worker item.
            restore_bound (bool, optional): Restore previous bounding box. Defaults to false
        """
        super().__init__()
        self.profile = profile
        self.worker = worker
        self._plot()

        # keep the global previous-bounding-box up to date
        @self.sigRangeChanged.connect
        def _():
            global previous_bounding_box
            previous_bounding_box = self.visibleRange()

        # restore the previous bounds if requested
        if restore_bound:
            global previous_bounding_box
            if previous_bounding_box is not None:
                self.setRange(previous_bounding_box)

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
