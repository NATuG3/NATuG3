import logging
from math import ceil, dist

import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QPen

import computers.datatypes
import settings
from computers.datatypes import NEMid
from constants.directions import *

logger = logging.getLogger(__name__)


class Plotter(pg.PlotWidget):
    """The main plot widget for the Plotter"""

    junctable_NEMid_clicked = pyqtSignal(computers.datatypes.NEMid)

    line_pen = pg.mkPen(color=settings.colors.grey)

    def __init__(self, worker):
        super().__init__()
        self.worker = worker
        self.worker.computed = self.worker.compute()

        # plot data
        self._plot()

        # set up styling
        self.setWindowTitle("Side View of DNA")  # set the window's title
        self.setBackground("w")  # make the background white

    def point_clicked(self, event, points):
        point = points[0]
        located = []
        for strand in self.worker.computed:
            for NEMid_ in strand:
                if dist(point.pos(), NEMid_.position()) < .01:
                    located.append(NEMid_)
        if len(located) == 2:
            self.junctable_NEMid_clicked.emit(NEMid_)
            logger.info(f"A junctable NEMid was clicked!\n{located}")

    def _plot(self):
        # we can calculate the axis scales at the end of generation;
        # we don't need to continuously recalculate the range
        self.disableAutoRange()

        for strand in self.worker.computed:
            symbols = []
            symbols_brushes = []
            x_coords = []
            z_coords = []

            for NEMid_ in strand:
                assert isinstance(NEMid_, NEMid)
                assert NEMid_.direction in (UP, DOWN)

                if NEMid_.direction == UP:
                    symbols.append("t1")  # up arrow
                    symbols_brushes.append(strand.color)
                elif NEMid_.direction == DOWN:
                    symbols.append("t")  # down arrow
                    symbols_brushes.append(strand.color)

                x_coords.append(NEMid_.x_coord)
                z_coords.append(NEMid_.z_coord)

            plotted = self.plot(  # actually plot the current strand of the current domain
                x_coords,
                z_coords,
                symbol=symbols,  # type of symbol (in this case up/down arrow)
                symbolSize=6,  # size of arrows in px
                pxMode=True,  # means that symbol size is in px
                symbolBrush=symbols_brushes,  # set color of points to current color
                pen=self.line_pen
            )

            plotted.sigPointsClicked.connect(self.point_clicked)

        # create pen for custom grid
        grid_pen: QPen = pg.mkPen(color=settings.colors.grey, width=1.4)

        # domain index grid
        for i in range(len(self.worker.domains) + 1):
            self.addLine(x=i, pen=grid_pen)

        # helical twist grid
        # overall_height = the tallest domain's height (the overall height of the plot's contents)
        overall_height = (
                max([domain.count for domain in self.worker.domains]) * self.worker.Z_b
        )
        # for i in <number of helical twists of the tallest domain>...
        for i in range(0, ceil(overall_height / self.worker.H) + 1):
            self.addLine(y=(i * self.worker.H), pen=grid_pen)

        # add axis labels
        self.setLabel("bottom", text="Helical Domain")
        self.setLabel("left", text="Helical Twists", units="nanometers")

        # re-enable auto-range so that it isn't zoomed out weirdly
        self.autoRange()
        # set custom X range of plot
        self.setXRange(0, len(self.worker.domains))
