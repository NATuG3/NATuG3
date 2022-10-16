import pyqtgraph as pg
import logging
from math import ceil
from constants.directions import *
from PyQt6.QtGui import QPen

logger = logging.getLogger(__name__)


class Plotter(pg.GraphicsLayoutWidget):
    """A widget that fetches current settings and generates helices side view."""

    def __init__(self, worker):
        super().__init__()
        self.worker = worker

        # set up styling
        self.setWindowTitle("Side View of DNA")  # set the window's title
        self.setBackground("w")  # make the background white

        # create and add the main plot
        self.plot = Plot(worker)
        self.addItem(self.plot)


class Plot(pg.PlotItem):
    """The main plot widget for the Plotter"""

    def __init__(self, worker):
        super().__init__()
        self.worker = worker

        # we can calculate the axis scales at the end of generation;
        # we don't need to continuously recalculate the range
        self.disableAutoRange()

        for index, domain in enumerate(worker.domains):
            if index % 2:  # if the domain index is an even integer
                colors: tuple = ((255, 0, 0), (0, 255, 0))  # use red and green colors
            else:  # but if it is an odd integer
                colors: tuple = (
                    (0, 0, 255),
                    (255, 255, 0),
                )  # use blue and yellow colors
            # this way it will be easy to discern between different domains
            # (every other domain will be a different color scheme)

            for strand_direction in (UP, DOWN):
                if strand_direction == UP:  # 0 means up strand
                    symbol: str = "t1"  # up arrow for up strand
                    color: str = colors[
                        0
                    ]  # set the color to be the second option of current color scheme (which is "colors")
                elif strand_direction == DOWN:  # 1 means down strand
                    symbol: str = "t"  # down arrow for down strand
                    color: str = colors[
                        1
                    ]  # set the color to be the first option of current color scheme (which is "colors")

                # obtain an array of x and z coords from the points container
                x_coords = self.worker.x_coords[index][strand_direction]
                z_coords = self.worker.z_coords[index][strand_direction]

                self.plot(  # actually plot the current strand of the current domain
                    x_coords,
                    z_coords,
                    symbol=symbol,  # type of symbol (in this case up/down arrow)
                    symbolSize=6,  # size of arrows in px
                    pxMode=True,  # means that symbol size is in px
                    symbolPen=pg.mkPen(
                        color=color
                    ),  # set color of points to current color
                    pen=pg.mkPen(
                        color=(120, 120, 120), width=1.8
                    ),  # set color of pen to current color (but darker)
                )

        # create pen for custom grid
        grid_pen: QPen = pg.mkPen(color=(220, 220, 220), width=1.4)

        # domain index grid
        for i in range(len(self.worker.domains) + 1):
            self.addLine(x=i, pen=grid_pen)

        # helical twist grid
        # overall_height = the tallest domain's height (the overall height of the plot's contents)
        overall_height = max([domain.count for domain in worker.domains]) * worker.Z_b
        # for i in <number of helical twists of the tallest domain>...
        for i in range(-1, ceil(overall_height / worker.H) + 2):
            self.addLine(y=(i * worker.H), pen=grid_pen)

        # add axis labels
        self.setLabel("bottom", text="Helical Domain", units="#")
        self.setLabel("left", text="Helical Twists", units="#")

        # re-enable auto-range so that it isn't zoomed out weirdly
        self.autoRange()
        # set custom X range of plot
        self.setXRange(0, len(self.worker.domains))
