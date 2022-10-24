import logging

import pyqtgraph as pg

logger = logging.getLogger(__name__)


class Plotter(pg.GraphicsLayoutWidget):
    def __init__(self, worker):
        super().__init__()

        # TopView object
        self.worker = worker

        # make the background white
        self.setBackground("w")

        # create and add the main plot
        self.plot = Plot(worker)
        self.addItem(self.plot)


class Plot(pg.PlotItem):
    """The main plot widget for the Plotter"""

    domain_brush = pg.mkBrush(color=(90, 90, 90))

    def __init__(self, worker):
        super().__init__()
        self.worker = worker

        # create main plot
        self.plot(
            self.worker.u_coords,
            self.worker.v_coords,
            symbol="o",
            symbolSize=self.worker.D,
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
