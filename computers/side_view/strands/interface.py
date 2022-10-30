import logging
from contextlib import suppress
from math import ceil, dist
from typing import List, Tuple

import pyqtgraph as pg
from PyQt6.QtGui import QPen

import references
import settings
from computers.side_view.strands.strand import Strand
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
        self.profile = profile

        self.plot_items = []
        self.graph_width = width
        self.graph_height = height

        self.disableAutoRange()
        self._plot()
        self.autoRange()
        self.setXRange(0, self.graph_width)
        self._prettify()

        # set up styling
        self.setWindowTitle("Side View of DNA")  # set the window's title

    def clear(self):
        for plot_item in self.plot_items:
            self.removeItem(plot_item)

    def refresh(self):
        self.clear()
        self._plot()

    def junctable_NEMid_clicked(self, NEMid1, NEMid2):
        """Called when a NEMid that could be made a junction is clicked."""
        self.strands.add_junction(NEMid1, NEMid2)
        references.strands = self.strands
        self.refresh()

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

    def _prettify(self):
        # create pen for custom grid
        grid_pen: QPen = pg.mkPen(color=settings.colors.grey, width=1.4)

        # domain index grid
        for i in range(len(self.strands.strands) * 2 + 1):
            self.addLine(x=i, pen=grid_pen)

        # for i in <number of helical twists of the tallest domain>...
        for i in range(0, ceil(self.graph_width / self.profile.H) + 1):
            self.addLine(y=(i * self.profile.H), pen=grid_pen)

        # add axis labels
        self.setLabel("bottom", text="Helical Domain")
        self.setLabel("left", text="Helical Twists", units="nanometers")

    def _plot(self):
        for strand in self.strands.strands:
            assert isinstance(strand, Strand)

            symbols: List[str] = []
            symbols_brushes: List[Tuple[int, int, int]] = []
            x_coords: List[float] = []
            z_coords: List[float] = []

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

            self.plot_items.append(
                (
                    self.plot(  # actually plot the current strand of the current domain
                        x_coords,
                        z_coords,
                        symbol=symbols,  # type of symbol (in this case up/down arrow)
                        symbolSize=6,  # size of arrows in px
                        pxMode=True,  # means that symbol size is in px and non-dynamic
                        symbolBrush=symbols_brushes,  # set color of points to current color
                        pen=self.line_pen,
                    )
                )
            )

            self.plot_items[-1].sigPointsClicked.connect(self.point_clicked)
