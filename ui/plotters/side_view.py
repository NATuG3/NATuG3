import logging
from contextlib import suppress
from dataclasses import dataclass, field
from math import ceil
from typing import List, Tuple, Dict, Literal

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal, QTimer, QVariant
from PyQt6.QtGui import (
    QPen,
)

import settings
from structures.points import NEMid, Nucleoside
from structures.points.point import Point
from structures.profiles import NucleicAcidProfile
from ui.plotters.utils import custom_symbol, chaikins_corner_cutting

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class PlotData:
    """
    Currently plotted data.

    Attributes:
        strands: The currently plotted strands.
        mode: The plotting toolbar. Either 'nucleoside' or 'NEMid'.
        points: A mapping of positions of plotted_points to point objects.
        plotted_points: The points.
        plotted_nicks: The nicks.
        plotted_linkages: The linkages.
        plotted_labels: All plotted text labels.
        plotted_strokes: The strand pen line.
        plotted_gridlines: All the grid lines.
    """

    strands: "Strands" = None
    mode: Literal["nucleoside", "NEMid"] = "NEMid"
    points: Dict[Tuple[float, float], "Point"] = field(default_factory=dict)
    plotted_points: List[pg.PlotDataItem] = field(default_factory=list)
    plotted_nicks: List[pg.PlotDataItem] = field(default_factory=list)
    plotted_linkages: List[pg.PlotDataItem] = field(default_factory=list)
    plotted_labels: List[pg.PlotDataItem] = field(default_factory=list)
    plotted_strokes: List[pg.PlotDataItem] = field(default_factory=list)
    plotted_gridlines: List[pg.PlotDataItem] = field(default_factory=list)


class SideViewPlotter(pg.PlotWidget):
    """
    Side view strands plot widget.

    Attributes:
        strands: The strands to plot.
        nucleic_acid_profile: The nucleic acid nucleic_acid_profile of the
            strands to plot.
        plot_data: Currently plotted data.
        width: The width of the plot.
        height: The height of the plot.
        mode: The plotting toolbar. Either "nucleoside" or "NEMid".

    Signals:
        points_clicked(tuple of all points clicked): When plotted points are clicked.
        strand_clicked(the strand that was clicked): When a strand is clicked.
    """

    points_clicked = pyqtSignal(object, arguments=("Clicked Point NEMids",))
    strand_clicked = pyqtSignal(object, arguments=("Clicked Strand",))
    linkage_clicked = pyqtSignal(object, arguments=("Clicked Linkages",))

    def __init__(
        self,
        strands: "Strands",
        nucleic_acid_profile: NucleicAcidProfile,
        mode: Literal["nucleoside", "NEMid"],
    ) -> None:
        """
        Initialize plotter instance.

        Args:
            strands: The strands to plot.
            nucleic_acid_profile: The nucleic acid nucleic_acid_profile of the
                strands to plot.
            mode: toolbar: The plotting toolbar. Either "nucleoside" or "NEMid".
        """
        super().__init__()

        # store config data
        self.strands = strands
        self.nucleic_acid_profile = nucleic_acid_profile
        self.mode = mode
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
        return self.plot_data.strands.size[1]

    @property
    def width(self):
        return self.plot_data.strands.size[0]

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
        for nick in plot_data.plotted_nicks:
            self.removeItem(nick)
        for linkage in plot_data.plotted_linkages:
            self.removeItem(linkage)
        for labels in plot_data.plotted_labels:
            self.removeItem(labels)
        for gridline in plot_data.plotted_gridlines:
            self.removeItem(gridline)
        self.clear()

    def _points_clicked(self, event, points):
        """Called when a point on a strand is clicked."""
        position = tuple(points[0].pos())
        self.points_clicked.emit(self.plot_data.points[position])

    def _prettify(self):
        """Add plotted_gridlines and style the plot."""
        # clear preexisting plotted_gridlines
        self.plot_data.plotted_gridlines = []

        # create pen for custom grid
        grid_pen: QPen = pg.mkPen(color=settings.colors["grid_lines"], width=1.4)

        # domain index grid
        for i in range(ceil(self.plot_data.strands.size[0]) + 1):
            self.plot_data.plotted_gridlines.append(self.addLine(x=i, pen=grid_pen))

        # for i in <number of helical twists of the tallest domain>...
        with suppress(ZeroDivisionError):
            for i in range(0, ceil(self.height / self.nucleic_acid_profile.H)):
                self.plot_data.plotted_gridlines.append(
                    self.addLine(y=(i * self.nucleic_acid_profile.H), pen=grid_pen)
                )

        # add axis labels
        self.setLabel("bottom", text="x", units="Helical Diameters")
        self.setLabel("left", text="z", units="Nanometers")

    def _plot(self):
        """
        Plot the side view.

        All plotted data gets saved in the current plot_data.

        Raises:
            ValueError: If the mode is not of type "nucleoside" or "NEMid".
        """
        from structures.strands.linkage import Linkage
        from structures.strands.strand import StrandItems

        self.plot_data.strands = self.strands
        self.plot_data.mode = self.mode
        self.plot_data.points.clear()
        self.plot_data.plotted_labels.clear()
        self.plot_data.plotted_points.clear()
        self.plot_data.plotted_nicks.clear()
        self.plot_data.plotted_linkages.clear()
        self.plot_data.plotted_strokes.clear()

        for strand_index, strand in enumerate(self.plot_data.strands.strands):
            # create containers for plotting data
            symbols: List[str] = list()
            symbol_sizes: List[int] = list()
            symbol_brushes = list()
            symbol_pens = list()
            x_coords: List[float] = list()
            z_coords: List[float] = list()

            # iterate on the proper type based on toolbar
            to_plot = strand.items.by_type((Point, Linkage))

            # now create the proper plot data for each point one by one
            for point_index, point in enumerate(to_plot):
                if isinstance(point, Linkage):
                    continue

                # store the point's coordinates
                x_coords.append(point.x_coord)
                z_coords.append(point.z_coord)

                # update the point mappings (this is a dict that allows us to easily
                # traverse between a coord and a Point)
                self.plot_data.points[(point.x_coord, point.z_coord)] = point

                # based on plot mode, some items may be plotted as small stars:
                if (
                    self.plot_data.mode == "NEMid" and isinstance(point, Nucleoside)
                ) or (self.plot_data.mode == "nucleoside" and isinstance(point, NEMid)):
                    symbols.append("o")
                    symbol_sizes.append(2)
                    symbol_brushes.append(pg.mkBrush(color=(30, 30, 30)))
                    symbol_pens.append(None)
                else:
                    # if the symbol is a custom symbol, use the custom symbol
                    if point.styles.symbol_is_custom():
                        symbols.append(
                            custom_symbol(
                                point.styles.symbol,
                                flip=False,
                                rotation=point.styles.rotation,
                            )
                        )
                    else:
                        symbols.append(point.styles.symbol)

                    # store the symbol size
                    symbol_sizes.append(point.styles.size)

                    # store the symbol brush
                    symbol_brushes.append(
                        pg.mkBrush(color=point.styles.fill, width=point.styles.outline[1])
                    )

                    # store the symbol pen
                    symbol_pens.append(
                        pg.mkPen(
                            color=point.styles.outline[0], width=point.styles.outline[1]
                        )
                    )

            # graph the points separately
            plotted_points = pg.PlotDataItem(
                x_coords,
                z_coords,
                symbol=symbols,  # type of symbol (in this case up/down arrow)
                symbolSize=symbol_sizes,  # size of arrows in px
                pxMode=True,  # means that symbol size is in px and non-dynamic
                symbolBrush=symbol_brushes,  # set color of points to current color
                symbolPen=symbol_pens,  # for the outlines of points
                pen=None,
            )
            plotted_points.sigPointsClicked.connect(self._points_clicked)
            self.plot_data.plotted_points.append(plotted_points)

            for stroke_segment in StrandItems(to_plot).split(Linkage):
                x_coords = [point.x_coord for point in stroke_segment]
                z_coords = [point.z_coord for point in stroke_segment]

                # if this strand contains a junction then
                # round the corners of the outline for aesthetics
                if strand.interdomain():
                    coords = zip(x_coords, z_coords)
                    coords = chaikins_corner_cutting(coords, offset=0.4, refinements=1)
                    coords = list(chaikins_corner_cutting(coords, refinements=1))

                    connect = []
                    # in case the junction is a left-to-right side of screen junction
                    # do not plot the entire connector line going from the left to the
                    # right of the screen
                    for point_index, (x_coord, z_coord) in enumerate(coords.copy()):
                        # if the distance between this x coord and the next one is large
                        # then add a break in the connector. Note that the "next x coord"
                        # to check against is typically the next on in the array,
                        # except when we reach the end of the list, in which case it
                        # becomes the first one.
                        if point_index != len(coords) - 1:
                            next_x_coord = coords[point_index + 1][0]
                        else:
                            next_x_coord = coords[0][0]

                        # if the distance between this x coord and the next one is large
                        # then don't add a connection. otherwise add a connection.
                        if abs(x_coord - next_x_coord) > 1:
                            # do not connect
                            connect.append(0)
                        else:
                            # connect
                            connect.append(1)

                    # closed strands will have one extra item in the end so that they
                    # appear connected
                    if strand.closed:
                        connect.append(1)

                    connect = np.array(connect)
                    x_coords = [coord[0] for coord in coords]
                    z_coords = [coord[1] for coord in coords]
                else:
                    connect = "all"

                # if the strand is closed then connect the last point to the first
                # point
                if strand.closed:
                    x_coords.append(x_coords[0])
                    z_coords.append(z_coords[0])

                # plot the outline
                plotted_stroke = pg.PlotDataItem(
                    x_coords,
                    z_coords,
                    pen=pg.mkPen(
                        color=strand.styles.color.value,
                        width=strand.styles.thickness.value,
                    ),
                    connect=connect,
                )

                plotted_stroke.setCurveClickable(True)
                plotted_stroke.sigClicked.connect(
                    lambda *args, to_emit=strand: self.strand_clicked.emit(to_emit)
                )
                self.plot_data.plotted_strokes.append(plotted_stroke)

                # Add the linkages to the plot
                for linkage in strand.items.by_type(Linkage):
                    # obtain the coords of the linkage
                    coords = linkage.plot_points
                    coords = chaikins_corner_cutting(coords, refinements=9)
                    x_coords = [coord[0] for coord in coords]
                    z_coords = [coord[1] for coord in coords]

                    # plot the linkage
                    plotted_linkage = pg.PlotDataItem(
                        x_coords,
                        z_coords,
                        pen=pg.mkPen(
                            color=linkage.styles.color, width=linkage.styles.thickness
                        ),
                    )
                    plotted_linkage.setCurveClickable(True)
                    plotted_linkage.sigClicked.connect(
                        lambda *args, to_emit=linkage: self.linkage_clicked.emit(
                            to_emit
                        )
                    )
                    self.plot_data.plotted_linkages.append(plotted_linkage)

        # Add the nicks to the plot
        nick_brush = pg.mkBrush(color=settings.colors["nicks"])
        for nick in self.plot_data.strands.nicks:
            plotted_nick = pg.PlotDataItem(
                (nick.x_coord,),
                (nick.z_coord,),
                symbol="o",
                symbolSize=8,
                pxMode=True,
                symbolBrush=nick_brush,
                symbolPen=None,
                pen=None,
            )
            self.plot_data.plotted_nicks.append(plotted_nick)
            self.plot_data.points[(nick.x_coord, nick.z_coord)] = nick
            plotted_nick.sigPointsClicked.connect(self._points_clicked)

        # Configure the order to add things to the plot
        # Note that the lower items are plotted last and therefore are on top
        layers = (
            self.plot_data.plotted_linkages,
            self.plot_data.plotted_strokes,
            self.plot_data.plotted_nicks,
            self.plot_data.plotted_points,
        )

        # Add the items to the plot
        for layer in layers:
            for item in layer:
                self.addItem(item)

        # Style the plot
        self._prettify()
