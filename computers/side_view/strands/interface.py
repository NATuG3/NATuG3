import logging
from math import ceil, dist
from typing import List

import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QPen

import settings
from constants.directions import *
from datatypes.misc import Profile
from datatypes.points import NEMid

logger = logging.getLogger(__name__)


class Plotter(pg.PlotWidget):
    """The references plot widget for the Plotter"""

    line_pen = pg.mkPen(color=settings.colors.grey)

    def __init__(self,
                 strands,  #: computers.side_view.strands.Strands
                 width: float,
                 height: float,
                 profile: Profile
                 ):
        """
        Initialize plotter instance.

        Args:
            strands: The actual side view worker item.
            width: Width of plot. In nanometers.
            height: Height of plot. In nanometers.
            profile: The settings profile to use for grid line computations.
        """
        super().__init__()
        self.strands = strands
        self._width = width
        self._height = height
        self.profile = profile
        self.disableAutoRange()
        self._plot()
        # for the first run compute a reasonable range
        self.autoRange()
        self.setXRange(0, self._width)

        # set up styling
        self.setWindowTitle("Side View of DNA")  # set the window's title

    def refresh(self):
        self.clear()
        self._plot()

    def clear(self):
        self.getPlotItem().clear()

    def junctable_NEMid_clicked(self, NEMid1, NEMid2):
        """Called when a NEMid that could be made a junction is clicked."""
        self.strands.add_junction()

    def point_clicked(self, event, points):
        """Called when a point on a strand is clicked."""
        point = points[0]
        located = []
        for strand in self.strands.strands:
            for NEMid_ in strand:
                if dist(point.pos(), NEMid_.position()) < settings.junction_threshold:
                    located.append(NEMid_)
        if len(located) == 2:
            logger.info(f"A junctable NEMid was clicked!\n{located}")
            self.junctable_NEMid_clicked(*located)

    def _plot(self):
        for strand in self.strands.strands:
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
        for i in range(len(self.strands.strands) * 2 + 1):
            self.addLine(x=i, pen=grid_pen)

        # for i in <number of helical twists of the tallest domain>...
        for i in range(0, ceil(self._height / self.profile.H) + 1):
            self.addLine(y=(i * self.profile.H), pen=grid_pen)

        # add axis labels
        self.setLabel("bottom", text="Helical Domain")
        self.setLabel("left", text="Helical Twists", units="nanometers")
