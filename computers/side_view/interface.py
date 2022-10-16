import logging
from math import ceil, dist

import pyqtgraph as pg
from PyQt6.QtGui import QPen
from PyQt6.QtCore import Qt, pyqtSignal

import computers.datatypes
import config
from constants.directions import *

logger = logging.getLogger(__name__)


class Plotter(pg.PlotWidget):
    """The main plot widget for the Plotter"""

    junctable_NEMid_clicked = pyqtSignal(computers.datatypes.NEMid)

    def __init__(self, worker):
        super().__init__()
        self.worker = worker
        self.worker.computed = self.worker.compute()

        # plot data
        self._plot()

        # set up styling
        self.setWindowTitle("Side View of DNA")  # set the window's title
        self.setBackground("w")  # make the background white

        self.scene().sigMouseClicked.connect(self.mouse_clicked)

    def mouse_clicked(self, event):
        if event.button() != Qt.MouseButton.LeftButton:
            return

        # obtain clicked coord
        # https://stackoverflow.com/a/70852527
        vb = self.plotItem.vb
        scene_coords = event.scenePos()
        if self.sceneBoundingRect().contains(scene_coords):
            clicked_coord = vb.mapSceneToView(scene_coords)
            clicked_coord = (clicked_coord.x(), clicked_coord.y())
        logger.info(f"Side view plot clicked @ {round(clicked_coord[0], 3), round(clicked_coord[1], 3)}")

        # check to see if this is a potential junction click
        if 0 < clicked_coord[0] < len(self.worker.domains):
            # scan both up and down strand of domain#round(x coord of click)
            for strand_direction in self.worker.strand_directions:
                # for each NEMid in that strand
                for NEMid in self.worker.computed[round(clicked_coord[0])][strand_direction]:
                    # if it is a NEMid that could be made into a junction
                    if NEMid.junctable:
                        # check to see if the click was close enough to the NEMid
                        if dist(NEMid.position, clicked_coord) < 0.08:
                            # if it was then this could be a junction!
                            logger.info(f"A junctable NEMid was clicked.\n{NEMid}")
                            self.junctable_NEMid_clicked.emit(NEMid)

    def _plot(self):
        # we can calculate the axis scales at the end of generation;
        # we don't need to continuously recalculate the range
        self.disableAutoRange()

        for index, domain in enumerate(self.worker.domains):
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
                x_coords = [NEMid.x_coord for NEMid in self.worker.computed[index][strand_direction]]
                z_coords = [NEMid.z_coord for NEMid in self.worker.computed[index][strand_direction]]

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
                        color=config.colors.grey, width=1.8
                    ),  # set color of pen to current color (but darker)
                )

        # create pen for custom grid
        grid_pen: QPen = pg.mkPen(color=config.colors.grey, width=1.4)

        # domain index grid
        for i in range(len(self.worker.domains) + 1):
            self.addLine(x=i, pen=grid_pen)

        # helical twist grid
        # overall_height = the tallest domain's height (the overall height of the plot's contents)
        overall_height = max([domain.count for domain in self.worker.domains]) * self.worker.Z_b
        # for i in <number of helical twists of the tallest domain>...
        for i in range(-1, ceil(overall_height / self.worker.H) + 2):
            self.addLine(y=(i * self.worker.H), pen=grid_pen)

        # add axis labels
        self.setLabel("bottom", text="Helical Domain", units="#")
        self.setLabel("left", text="Helical Twists", units="#")

        # re-enable auto-range so that it isn't zoomed out weirdly
        self.autoRange()
        # set custom X range of plot
        self.setXRange(0, len(self.worker.domains))
