import logging
from math import ceil, dist
from typing import List

import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QPen

import settings
from computers.side_view.strands.strand import Strand
from constants.directions import *
from datatypes.misc import Profile
from datatypes.points import NEMid

logger = logging.getLogger(__name__)

previous_bounding_box = None


class Plotter(pg.PlotWidget):
    """The references plot widget for the Plotter"""

    junctable_NEMid_clicked = pyqtSignal(NEMid)

    line_pen = pg.mkPen(color=settings.colors.grey)

    def __init__(self,
                 strands: List[Strand],
                 width: float,
                 height: float,
                 profile: Profile,
                 restore_bound: bool = False):
        """
        Initialize plotter instance.

        Args:
            strands: The actual side view worker item.
            width: Width of plot. In nanometers.
            height: Height of plot. In nanometers.
            profile: The settings profile to use for grid line computations.
            restore_bound: Restore previous bounding box. Defaults to false
        """
        super().__init__()
        self.strands = strands
        self._width = width
        self._height = height
        self.profile = profile
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

        # set up styling
        self.setWindowTitle("Side View of DNA")  # set the window's title

    def point_clicked(self, event, points):
        point = points[0]
        located = []
        for strand in self.strands:
            for NEMid_ in strand:
                if dist(point.pos(), NEMid_.position()) < settings.junction_threshold:
                    located.append(NEMid_)
        if len(located) == 2:
            self.junctable_NEMid_clicked.emit(NEMid_)
            logger.info(f"A junctable NEMid was clicked!\n{located}")

    def _plot(self):
        # we can calculate the axis scales at the end of generation;
        # we don't need to continuously recalculate the range
        self.disableAutoRange()

        for strand in self.strands:
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

            plotted = (
                self.plot(  # actually plot the current strand of the current domain
                    x_coords,
                    z_coords,
                    symbol=symbols,  # type of symbol (in this case up/down arrow)
                    symbolSize=6,  # size of arrows in px
                    pxMode=True,  # means that symbol size is in px
                    symbolBrush=symbols_brushes,  # set color of points to current color
                    pen=self.line_pen,
                )
            )

            plotted.sigPointsClicked.connect(self.point_clicked)

        # create pen for custom grid
        grid_pen: QPen = pg.mkPen(color=settings.colors.grey, width=1.4)

        # domain index grid
        for i in range(len(self.strands)*2 + 1):
            self.addLine(x=i, pen=grid_pen)

        # for i in <number of helical twists of the tallest domain>...
        for i in range(0, ceil(self._height / self.profile.H) + 1):
            self.addLine(y=(i * self.profile.H), pen=grid_pen)

        # add axis labels
        self.setLabel("bottom", text="Helical Domain")
        self.setLabel("left", text="Helical Twists", units="nanometers")

        # re-enable auto-range so that it isn't zoomed out weirdly
        self.autoRange()
        # set custom X range of plot
        self.setXRange(0, self._width)
