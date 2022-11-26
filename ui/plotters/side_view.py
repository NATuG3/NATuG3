import logging
from contextlib import suppress
from dataclasses import dataclass
from functools import partial
from math import ceil, dist
from typing import List, Type, Tuple, Dict

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import (
    QPen,
)

import settings
from constants.directions import *
from helpers import chaikins_corner_cutting
from structures.points import NEMid
from structures.points.point import Point
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
        types: The types of strand NEMids plotted.
        points: A mapping of positions of plotted_points to point objects.
        plotted_points: The points.
        plotted_strokes: The strand pen line.
        plotted_gridlines: All the grid lines.
    """

    strands: Strands = None
    types: List[Type] = None
    points: Dict[Tuple[float, float], Point] = None
    plotted_points: List[pg.PlotDataItem] = None
    plotted_strokes: List[pg.PlotDataItem] = None
    plotted_gridlines: List[pg.PlotDataItem] = None


class SideViewPlotter(pg.PlotWidget):
    """
    Side view strands plot widget.

    Attributes:
        strands: The strands to plot.
        nucleic_acid_profile: The nucleic acid nucleic_acid_profile of the strands to plot.
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
            nucleic_acid_profile: The nucleic acid nucleic_acid_profile of the strands to plot.
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
        for stroke in plot_data.plotted_strokes:
            self.removeItem(stroke)
        for points in plot_data.plotted_points:
            self.removeItem(points)
        for gridline in plot_data.plotted_gridlines:
            self.removeItem(gridline)

    def _points_clicked(self, event, points):
        """Called when a point on a strand is clicked."""
        position = tuple(points[0].pos())

        # use point mapping to detect the clicked points
        located = [self.plot_data.points[position]]
        # if the located item is a NEMid with a juncmate append the juncmate too
        if isinstance(located[0], NEMid) and (located[0].juncmate is not None):
            located.append(located[0].juncmate)

        # remove all pseduo items
        for item in located:
            with suppress(AttributeError):
                if item.pseudo:
                    located.remove(item)

        self.points_clicked.emit(tuple(located))

    def _prettify(self):
        """Add plotted_gridlines and style the plot."""
        # clear preexisting plotted_gridlines
        self.plot_data.plotted_gridlines = []

        # create pen for custom grid
        grid_pen: QPen = pg.mkPen(color=settings.colors["grid_lines"], width=1.4)

        # domain index grid
        for i in range(ceil(self.strands.size[0]) + 1):
            self.plot_data.plotted_gridlines.append(self.addLine(x=i, pen=grid_pen))

        # for i in <number of helical twists of the tallest domain>...
        for i in range(0, ceil(self.height / self.nucleic_acid_profile.H) + 1):
            self.plot_data.plotted_gridlines.append(
                self.addLine(y=(i * self.nucleic_acid_profile.H), pen=grid_pen)
            )

        # add axis labels
        self.setLabel("bottom", text="Helical Domain")
        self.setLabel("left", text="Helical Twists", units="nanometers")

    def _plot(self):
        self.plot_data.strands = self.strands
        self.plot_data.types = self.plot_types
        self.plot_data.points = dict()
        self.plot_data.plotted_points = list()
        self.plot_data.plotted_strokes = list()

        for strand_index, strand in enumerate(self.plot_data.strands.strands):
            # use a try finally to ensure that the pseudo NEMid at the end of the strand is removed
            if strand.closed:
                strand.NEMids.append(strand.NEMids[0])
                strand.NEMids[-1].pseudo = True

            symbols: List[str] = list()
            symbol_sizes: List[int] = list()
            x_coords: List[float] = list()
            z_coords: List[float] = list()
            brushes = list()

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

            for NEMid_index, NEMid_ in enumerate(strand.NEMids):
                # update the point mappings
                self.plot_data.points[
                    (
                        NEMid_.x_coord,
                        NEMid_.z_coord,
                    )
                ] = NEMid_

                # ensure that this NEMid gets plotted
                x_coords.append(NEMid_.x_coord)
                z_coords.append(NEMid_.z_coord)

                # determine whether the symbol for the NEMid is an up or down arrow
                if NEMid_.direction == UP:
                    symbols.append("t1")  # up arrow
                elif NEMid_.direction == DOWN:
                    symbols.append("t")  # down arrow
                else:
                    raise ValueError("NEMid.direction is not UP or DOWN.", NEMid_)

                # if the NEMid is highlighted then make it larger and yellow
                if NEMid_.highlighted:
                    symbol_sizes.append(18)
                    brushes.append(pg.mkBrush(color=settings.colors["highlighted"]))
                else:
                    symbol_sizes.append(6)
                    # if the NEMid is junctable then make it dimmer colored
                    if NEMid_.junctable:
                        brushes.append(dim_brush)
                    # otherwise use normal coloring
                    else:
                        brushes.append(NEMid_brush)

            # graph the points separately
            plotted_points = pg.PlotDataItem(
                x_coords,
                z_coords,
                symbol=symbols,  # type of symbol (in this case up/down arrow)
                symbolSize=symbol_sizes,  # size of arrows in px
                pxMode=True,  # means that symbol size is in px and non-dynamic
                symbolBrush=brushes,  # set color of points to current color
                pen=None,
            )
            plotted_points.sigPointsClicked.connect(self._points_clicked)
            self.plot_data.plotted_points.append(plotted_points)

            # if this strand contains a junction then
            # round the corners of the outline for aesthetics
            if strand.interdomain:
                coords = zip(x_coords, z_coords)
                coords = chaikins_corner_cutting(coords, offset=0.4, refinements=1)
                coords = list(chaikins_corner_cutting(coords, refinements=1))

                connect = []
                # in case the junction is a left-to-right side of screen junction
                # do not plot the entire connector line going from the left to the
                # right of the screen
                for NEMid_index, (x_coord, z_coord) in enumerate(coords.copy()):
                    if NEMid_index != len(coords) - 1:
                        # if the distance between this x coord and the next one is large
                        # then add a break in the connector
                        if abs(x_coord - coords[NEMid_index + 1][0]) > 1:
                            # do not connect
                            connect.append(0)
                        else:
                            connect.append(1)
                            # connect
                    else:
                        connect.append(1)

                connect = np.array(connect)
                x_coords = [coord[0] for coord in coords]
                z_coords = [coord[1] for coord in coords]
            else:
                connect = "all"

            # plot the outline separately
            stroke = pg.PlotDataItem(x_coords, z_coords, pen=pen, connect=connect)
            stroke.setCurveClickable(True)
            stroke.sigClicked.connect(partial(self.strand_clicked.emit, strand))
            self.plot_data.plotted_strokes.append(stroke)

        for stroke, points in zip(
            self.plot_data.plotted_strokes, self.plot_data.plotted_points
        ):
            self.addItem(stroke)
            self.addItem(points)

        self._prettify()
