import logging
from contextlib import suppress
from dataclasses import dataclass
from functools import partial
from math import ceil, dist
from typing import List, Type

import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import (
    QPen,
)

import settings
from constants.directions import *
from helpers import chaikins_corner_cutting
from structures.profiles import NucleicAcidProfile
from structures.strands import Strands
from structures.strands.strand import Strand

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class PlotData:
    """
    Currently plotted data.

    Attributes:
        strands: The currently plotted strands.
        points: The points.
        strokes: The strand pen line.
        plot_types: The types of strand NEMids plotted.
    """

    strands: Strands = None
    points: List[pg.PlotDataItem] = None
    strokes: List[pg.PlotDataItem] = None
    plot_types: List[Type] = None


class SideViewPlotter(pg.PlotWidget):
    """
    Side view strands plot widget.

    Attributes:
        strands: The strands to plot.
        nucleic_acid_profile: The nucleic acid profile of the strands to plot.
        plot_data: Currently plotted data.
        width: The width of the plot.
        height: The height of the plot.
        plot_types: The types of strand NEMids to plot.

    Signals:
        points_clicked(tuple of all points clicked): When plotted points are clicked.
        strand_clicked(the strand that was clicked): When a strand is clicked.
    """

    points_clicked = pyqtSignal(tuple, arguments=("Clicked Point NEMids",))
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
            plot_types: A list of the types of strand NEMids to plot. Defaults to all NEMids.
        """
        super().__init__()

        # store config data
        self.strands = strands
        self.nucleic_acid_profile = nucleic_acid_profile
        self.plot_types = plot_types
        self.plot_data = PlotData()

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

    def refresh(self):
        """Replot plot data."""
        def runner():
            self._reset()
            self._plot()
        # allow one screen refresh for the mouse to release
        # so that the plot is cleared after the mouse release event happens
        QTimer.singleShot(0, runner)
        logger.info("Refreshed side view.")

    def _reset(self, plot_data=None):
        """Clear plot_data from plot. Plot_data defaults to self.plot_data."""
        if plot_data is None:
            plot_data = self.plot_data
        for stroke in plot_data.strokes:
            self.removeItem(stroke)
        for points in plot_data.points:
            self.removeItem(points)

    def _points_clicked(self, event, points):
        """Called when a point on a strand is clicked."""
        position = points[0].pos()
        located = []
        for strand in self.strands.strands:
            for NEMid_ in strand.NEMids:
                if dist(position, NEMid_.position()) < settings.junction_threshold:
                    located.append(NEMid_)
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
        self.plot_data.strands = self.strands
        self.plot_data.plot_types = self.plot_types
        self.plot_data.points = []
        self.plot_data.strokes = []

        for strand in self.plot_data.strands.strands:
            # use a try finally to ensure that the pseudo NEMid at the end of the strand is removed
            if strand.closed:
                strand.NEMids.append(strand.NEMids[0])
                strand.NEMids[-1].pseudo = True

            symbols: List[str] = []
            symbol_sizes: List[int] = []
            x_coords: List[float] = []
            z_coords: List[float] = []
            brushes = []

            # create the NEMid brush
            NEMid_brush = pg.mkBrush(color=strand.color)

            # set dim brush as a dimmer version of the strand color
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

            for index, NEMid_ in enumerate(strand.NEMids):
                x_coords.append(NEMid_.x_coord)
                z_coords.append(NEMid_.z_coord)

                if NEMid_.direction == UP:
                    symbols.append("t1")  # up arrow
                elif NEMid_.direction == DOWN:
                    symbols.append("t")  # down arrow
                else:
                    raise ValueError("NEMid.direction is not UP or DOWN.", NEMid_)

                if NEMid_.highlighted:
                    symbol_sizes.append(18)
                    brushes.append(pg.mkBrush(color=settings.colors["highlighted"]))
                else:
                    if NEMid_.junctable:
                        brushes.append(dim_brush)
                        symbol_sizes.append(6)
                    else:
                        brushes.append(NEMid_brush)
                        symbol_sizes.append(6)

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
            points.sigPointsClicked.connect(self._points_clicked)
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
            self.plot_data.strokes.append(stroke)

            strand.clear_pseudos()

        for stroke, points in zip(self.plot_data.strokes, self.plot_data.points):
            self.addItem(stroke)
            self.addItem(points)

        self._prettify()
