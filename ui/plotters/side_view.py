import logging
from contextlib import suppress
from copy import copy
from functools import partial
from math import ceil, dist
from typing import List, Tuple

import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import (
    QPen,
)

import settings
from constants.directions import *
from helpers import chaikins_corner_cutting
from structures.points import NEMid
from structures.points.nick import Nick
from structures.profiles import NucleicAcidProfile
from structures.strands import Strands
from structures.strands.strand import Strand

logger = logging.getLogger(__name__)


class SideViewPlotter(pg.PlotWidget):
    """The refs plot widget for the Plotter"""

    points_clicked = pyqtSignal(tuple)
    strand_clicked = pyqtSignal(Strand)

    def __init__(self, strands: Strands, nucleic_acid_profile: NucleicAcidProfile):
        """Initialize plotter instance."""
        super().__init__()

        self.strands = strands
        self.nucleic_acid = nucleic_acid_profile

        self.plot_items = []
        self._width = lambda: self.strands.size[0]
        self._height = lambda: self.strands.size[1]

        self.disableAutoRange()
        self._plot()
        self.autoRange()
        self.setXRange(0, self._width())
        self._prettify()

        # set up styling
        self.setWindowTitle("Side View of DNA")  # set the window's title

    def clear(self):
        for plot_item in self.plot_items:
            self.removeItem(plot_item)

    def refresh(self):
        self.clear()
        self._plot()
        logger.info("Refreshed side view.")

    def _points_clicked(self, event, points):
        """Called when a point on a strand is clicked."""
        point = points[0]
        located = []
        for strand in self.strands.strands:
            for item in strand.items:
                if dist(point.pos(), item.position()) < settings.junction_threshold:
                    located.append(item)
        for item in located:
            with suppress(AttributeError):
                if item.pseudo:
                    located.remove(item)

        self.points_clicked.emit(tuple(located))

    def _prettify(self):
        # create pen for custom grid
        grid_pen: QPen = pg.mkPen(color=settings.colors["grid_lines"], width=1.4)

        # domain index grid
        for i in range(ceil(self.strands.size[0]) + 1):
            self.addLine(x=i, pen=grid_pen)

        # for i in <number of helical twists of the tallest domain>...
        for i in range(0, ceil(self._height() / self.nucleic_acid.H) + 1):
            self.addLine(y=(i * self.nucleic_acid.H), pen=grid_pen)

        # add axis labels
        self.setLabel("bottom", text="Helical Domain")
        self.setLabel("left", text="Helical Twists", units="nanometers")

    def _plot(self):
        plotted: List[Tuple[pg.PlotDataItem, pg.PlotDataItem]] = []

        for _strand in self.strands.strands:
            strand = copy(_strand)
            assert isinstance(strand, Strand)

            if strand.closed:
                strand.items.append(strand.items[0])
                strand.items[-1].pseudo = True

            symbols: List[str] = []
            symbol_sizes: List[int] = []
            x_coords: List[float] = []
            z_coords: List[float] = []
            brushes = []

            NEMid_brush = pg.mkBrush(color=strand.color)
            nick_brush = pg.mkBrush(color=(settings.colors["nicks"]))

            dim_brush = []
            for pigment in strand.color:
                pigment += 230
                if pigment > 255:
                    pigment = 255
                dim_brush.append(pigment)
            dim_brush = pg.mkBrush(color=dim_brush)

            if not strand.interdomain:
                pen = pg.mkPen(color=strand.color, width=2, pxMode=False)
            else:
                pen = pg.mkPen(color=strand.color, width=9.5, pxMode=False)

            for index, item in enumerate(strand.items):
                x_coords.append(item.x_coord)
                z_coords.append(item.z_coord)

                if isinstance(item, NEMid):
                    if item.direction == UP:
                        symbols.append("t1")  # up arrow
                    elif item.direction == DOWN:
                        symbols.append("t")  # down arrow
                    else:
                        raise ValueError("item.direction is not UP or DOWN.", item)

                    if item.highlighted:
                        symbol_sizes.append(18)
                        brushes.append(pg.mkBrush(color=settings.colors["highlighted"]))
                    else:
                        if item.junctable:
                            brushes.append(dim_brush)
                            symbol_sizes.append(6)
                        else:
                            brushes.append(NEMid_brush)
                            symbol_sizes.append(6)

                elif isinstance(item, Nick):
                    symbol_sizes.append(15)
                    symbols.append("o")
                    brushes.append(nick_brush)

            # graph the points separately
            points = pg.PlotDataItem(
                x_coords,
                z_coords,
                symbol=symbols,  # type of symbol (in this case up/down arrow)
                symbolSize=symbol_sizes,  # size of arrows in px
                pxMode=True,  # means that symbol size is in px and non-dynamic
                symbolBrush=brushes,  # set color of points to current color
                pen=None,
            )

            # if this strand contains a junction then
            # round the corners of the outline for aesthetics
            if strand.interdomain:
                coords = chaikins_corner_cutting(
                    tuple(zip(x_coords, z_coords)), offset=0.4, refinements=1
                )
                coords = chaikins_corner_cutting(coords, refinements=1)
                x_coords = [coord[0] for coord in coords]
                z_coords = [coord[1] for coord in coords]

            outline = pg.PlotDataItem(
                x_coords,
                z_coords,
                pen=pen,
            )
            outline.setCurveClickable(True)
            outline.sigClicked.connect(partial(self.strand_clicked.emit, _strand))

            plotted.append(
                (
                    outline,
                    points,
                )
            )

        for outline_only, points_only in plotted:
            # plot the outline
            self.addItem(outline_only)
            self.plot_items.append(outline_only)

            # plot the points
            self.addItem(points_only)
            # add trigger to points
            points_only.sigPointsClicked.connect(self._points_clicked)
            self.plot_items.append(points_only)

        self._prettify()
