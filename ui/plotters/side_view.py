import logging
from contextlib import suppress
from copy import copy
from dataclasses import dataclass
from functools import partial
from math import ceil, dist
from typing import List, Tuple, Type

import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import (
    QPen,
)
from pyqtgraph import PlotItem, PlotDataItem

import settings
from constants.directions import *
from helpers import chaikins_corner_cutting
from structures.points import NEMid, Nucleoside
from structures.points.nick import Nick
from structures.profiles import NucleicAcidProfile
from structures.strands import Strands
from structures.strands.strand import Strand

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class PlotData:
    """
    Currently plotted data.

    Attributes:
        points: The points.
        stroke: The strand pen line.
        plot_types: The types of strand items plotted.
    """
    points: PlotDataItem | None
    stroke: PlotDataItem | None
    plot_types: List[Type] | None


class SideViewPlotter(pg.PlotWidget):
    """
    Side view strands plot widget.

    Attributes:
        strands: The strands to plot.
        nucleic_acid_profile: The nucleic acid profile of the strands to plot.
        plot_data: Currently plotted data.
        width: The width of the plot.
        height: The height of the plot.
        plot_types: The types of strand items to plot.

    Signals:
        points_clicked(tuple of all points clicked): When plotted points are clicked.
        strand_clicked(the strand that was clicked): When a strand is clicked.
    """

    points_clicked = pyqtSignal(tuple, arguments=("Clicked Point items",))
    strand_clicked = pyqtSignal(Strand, arguments=("Clicked Strand",))

    def __init__(
        self,
        strands: Strands,
        nucleic_acid_profile: NucleicAcidProfile,
        plot_types: List[Type] = (object,),
    ):
        """
        Initialize plotter instance.

        Args:
            strands: The strands to plot.
            nucleic_acid_profile: The nucleic acid profile of the strands to plot.
            plot_types: A list of the types of strand items to plot. Defaults to all items.
        """
        super().__init__()

        # store config data
        self.strands = strands
        self.nucleic_acid_profile = nucleic_acid_profile
        self.plot_types = plot_types
        self.plot_data = PlotData(
            points=None,
            stroke=None,
            plot_types=self.plot_types
        )

        # plot initial data
        self.disableAutoRange()
        self._plot()
        self.autoRange()
        self.setXRange(0, self.width)
        self._prettify()

        # set up styling
        self.setWindowTitle("Side View of DNA")  # set the window's title

    @property
    def height(self):
        return self.strands.size[1]

    @property
    def width(self):
        return self.strands.size[0]

    def clear(self):
        self.removeItem(self.plot_data.stroke)
        self.removeItem(self.plot_data.points)

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
        for i in range(0, ceil(self.height / self.nucleic_acid_profile.H) + 1):
            self.addLine(y=(i * self.nucleic_acid_profile.H), pen=grid_pen)

        # add axis labels
        self.setLabel("bottom", text="Helical Domain")
        self.setLabel("left", text="Helical Twists", units="nanometers")

    def _plot(self):
        self.plot_data.points = []
        self.plot_data.stroke = []
        self.plot_data.plot_types = self.plot_types

        for strand in self.strands.strands:
            # use a try finally to ensure that the pseudo item at the end of the strand is removed
            try:
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

                # if it is an interdomain strand make the stroke thicker
                if not strand.interdomain:
                    pen = pg.mkPen(color=strand.color, width=2, pxMode=False)
                else:
                    pen = pg.mkPen(color=strand.color, width=9.5, pxMode=False)

                for index, item in enumerate(strand.items):
                    # only plot items of requested type
                    type_approved = False
                    for plot_type in self.plot_types:
                        if isinstance(item, plot_type):
                            type_approved = True
                            break
                    if not type_approved:
                        continue

                    x_coords.append(item.x_coord)
                    z_coords.append(item.z_coord)

                    # special plotting instructions for NEMids
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

                    # special plotting instructions for Nicks
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
                self.plot_data.points.append(points)

                # if this strand contains a junction then
                # round the corners of the outline for aesthetics
                if strand.interdomain:
                    coords = chaikins_corner_cutting(
                        tuple(zip(x_coords, z_coords)), offset=0.4, refinements=1
                    )
                    coords = chaikins_corner_cutting(coords, refinements=1)
                    x_coords = [coord[0] for coord in coords]
                    z_coords = [coord[1] for coord in coords]

                # plot the outline separately
                stroke = pg.PlotDataItem(
                    x_coords,
                    z_coords,
                    pen=pen,
                )
                stroke.setCurveClickable(True)
                stroke.sigClicked.connect(partial(self.strand_clicked.emit, strand))
                self.plot_data.stroke.append(stroke)

            finally:
                del strand.items[-1]

            for stroke, points in zip(self.plot_data.stroke, self.plot_data.points):
                # plot the outline
                self.addItem(stroke)

                # plot the points
                self.addItem(points)
                # add trigger to points
                points.sigPointsClicked.connect(self._points_clicked)

            self._prettify()

