import pyqtgraph as pg
import logging

logger = logging.getLogger(__name__)


class Plotter(pg.GraphicsLayoutWidget):
    def __init__(self, worker):
        super().__init__()

        # TopView object
        self.worker = worker

        # make the background white
        self.setBackground("w")

        self.plot = self.addPlot()

        self.plot.plot(
            self.worker.u_coords,
            self.worker.v_coords,
            symbol="o",
            symbolSize=self.worker.D,
            pxMode=False,
        )

        # increase the view box padding, since... our symbols are VERY large circles and pyqtgraph calculates padding
        # from the actual points, so the circles get cut off
        plotted_view_box = self.plot.getViewBox()
        plotted_view_box.setDefaultPadding(padding=0.18)

        # prevent user from interacting with the graph
        plotted_view_box.setAspectLocked(lock=True, ratio=1)
