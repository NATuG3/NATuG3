import pyqtgraph as pg
import logging
from constants.directions import *


logger = logging.getLogger(__name__)


class Plotter(pg.GraphicsLayoutWidget):
    """A widget that fetches current settings and generates helices side view."""

    def __init__(self, worker):
        super().__init__()
        self.worker = worker

        # set up styling
        self.setWindowTitle("Side View of DNA")  # set the window's title
        self.setBackground("w")  # make the background white
        self.plot: pg.plot = self.addPlot()

        # we can calculate the axis scales at the end of generation;
        # we don't need to continuously recalculate the range
        self.plot.disableAutoRange()

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

                self.plot.plot(  # actually plot the current strand of the current domain
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

        self.plot.autoRange()  # reenable autorange so that it isn't zoomed out weirdly
        self.plot.setXRange(0, len(self.worker.domains))
