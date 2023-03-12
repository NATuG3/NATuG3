import logging
from contextlib import suppress
from dataclasses import dataclass, field
from math import ceil
from typing import List, Tuple, Dict, Literal

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal, QTimer
from PyQt6.QtGui import QPen, QBrush, QPainterPath

import settings
from structures.points import NEMid, Nucleoside
from structures.points.point import Point, PointStyles
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

        self.plot_data.strands = self.strands
        self.plot_data.mode = self.mode
        self.plot_data.points.clear()
        self.plot_data.plotted_labels.clear()
        self.plot_data.plotted_points.clear()
        self.plot_data.plotted_nicks.clear()
        self.plot_data.plotted_linkages.clear()
        self.plot_data.plotted_strokes.clear()

        for strand_index, strand in enumerate(self.plot_data.strands.strands):
            # First plot all the points
            to_plot = strand.items.by_type(Point)

            # create containers for plotting data
            symbols = np.empty(len(to_plot), dtype=object)
            symbol_sizes = np.empty(len(to_plot), dtype=int)
            symbol_brushes = np.empty(len(to_plot), dtype=QBrush)
            symbol_pens = np.empty(len(to_plot), dtype=QPen)
            x_coords = np.empty(len(to_plot), dtype=float)
            z_coords = np.empty(len(to_plot), dtype=float)

            # now create the proper plot data for each point one by one
            for point_index, point in enumerate(to_plot):
                # Store the point's coordinates.
                x_coords[point_index] = point.x_coord
                z_coords[point_index] = point.z_coord

                # Update the point mappings. This is a dict that allows us to map the
                # location of a given point to the point object itself.
                self.plot_data.points[(point.x_coord, point.z_coord)] = point

                # If the point type is NOT the same as the active point type, use the
                # current styles of the point. Otherwise, plot a smaller "o" shaped
                # point to indicate that the point is not the active point type,
                # but still exists.
                if (
                    self.plot_data.mode == "NEMid" and isinstance(point, Nucleoside)
                ) or (self.plot_data.mode == "nucleoside" and isinstance(point, NEMid)):
                    symbols[point_index] = "o"
                    symbol_sizes[point_index] = 2
                    symbol_brushes[point_index] = pg.mkBrush(color=(30, 30, 30))
                    symbol_pens[point_index] = None
                else:
                    # if the symbol is a custom symbol, use the custom symbol
                    if point.styles.symbol_is_custom():
                        symbols[point_index] = custom_symbol(
                            point.styles.symbol,
                            flip=False,
                            rotation=point.styles.rotation,
                        )
                        assert isinstance(symbols[point_index], QPainterPath), (
                            "Custom symbol must be of type QPainterPath, but is of type"
                            f" {type(symbols[point_index])}"
                        )
                    else:
                        assert point.styles.symbol in PointStyles.all_symbols, (
                            f'Symbol "{point.styles.symbol} "is not a valid symbol. '
                            "Valid symbols are: "
                            f"{PointStyles.all_symbols}"
                        )
                        symbols[point_index] = point.styles.symbol

                    # Store the symbol size
                    symbol_sizes[point_index] = point.styles.size

                    # Create a brush for the symbol, based on the point's styles.
                    symbol_brushes[point_index] = pg.mkBrush(
                        color=point.styles.fill, width=point.styles.outline[1]
                    )

                    # Create a pen for the symbol, based on the point's styles.
                    symbol_pens[point_index] = pg.mkPen(
                        color=point.styles.outline[0], width=point.styles.outline[1]
                    )

            # Graph the plot for the points and for the strokes separately. First we
            # will plot the points.
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
            # When a point is clicked, invoke the _points_clicked method.
            plotted_points.sigPointsClicked.connect(self._points_clicked)
            self.plot_data.plotted_points.append(plotted_points)

            # A strand consists of items connected by a visual stroke. However,
            # linkages receive a special stroke that has a special color, style,
            # onClick method, and more. So, right now we will split all the strand
            # items into subunits of points, discluding linkages. These subunits can
            # be plotted as connected points with a single stroke each.
            for stroke_segment in strand.items.by_type(Point, Linkage).split(Linkage):
                if len(stroke_segment) > 0:
                    # Gather an array of all the x and z coordinates of the points in
                    # the stroke segment.
                    x_coords = [point.x_coord for point in stroke_segment]
                    z_coords = [point.z_coord for point in stroke_segment]

                    # Use the first point to fetch the number of total domains that are
                    # currently in existence.
                    domain_count = stroke_segment[0].domain.parent.parent.count

                    # If the strand is closed, we will be adding a pseudo point to the
                    # end of the stroke segment. If the last point and the first point
                    # are near in x value, then we will connect the last point to
                    # the first point (connect[-1] = True). Otherwise, we will not
                    # connect the last point to the first point (connect[-1] = False).
                    add_connected_pseudo_point = strand.closed and (
                        abs(stroke_segment[0].domain - stroke_segment[-1].domain)
                        == domain_count - 1
                    )

                    # If the point that proceeds a given point is in the last domain,
                    # and the point being proceeded is in the first domain, then the
                    # points are indeed continuous, but we don't want a line going
                    # across the screen. If we know that a strand is not interdomain
                    # (does not contain points within different domains, however,
                    # we can skip this check and connect all the points.
                    if not strand.interdomain():
                        connect = "all"
                    else:
                        # If the strand is closed, a pseudo point will be added to
                        # the end of the stroke segment. Whether this point gets a
                        # connection depends on the "add_connected_pseudo_point"
                        # variable.
                        if strand.closed:
                            # If the strand is closed, then we need to add a pseudo
                            # point to the end of the stroke segment.
                            connect = np.empty(len(stroke_segment) + 1, dtype=bool)
                        else:
                            # If the strand is not closed, then we don't need to add a
                            # pseudo point to the end of the stroke segment.
                            connect = np.empty(len(stroke_segment), dtype=bool)

                        for index, point in enumerate(stroke_segment[:-1]):
                            connect[index] = (
                                abs(point.domain - stroke_segment[index + 1].domain)
                                != domain_count - 1
                            )

                        # If the strand is closed then connect the last point to the
                        # first point by creating a pseudo-point at the first point's
                        # location. This will give the appearance of a closed strand.
                        if strand.closed:
                            connect[-1] = add_connected_pseudo_point
                            x_coords.append(x_coords[0])
                            z_coords.append(z_coords[0])

                    # Create the actual plot data item for the stroke segment.
                    plotted_stroke = pg.PlotDataItem(
                        x_coords,
                        z_coords,
                        pen=pg.mkPen(  # Create pen for the stroke from strand styles
                            color=strand.styles.color.value,
                            width=strand.styles.thickness.value,
                        ),
                        connect=connect,
                    )
                    # Make it so that the stroke itself can be clicked.
                    plotted_stroke.setCurveClickable(True)
                    # When the stroke is clicked, emit the strand_clicked signal. This
                    # will lead to the creation of a StrandConfig dialog.
                    plotted_stroke.sigClicked.connect(
                        lambda *args, to_emit=strand: self.strand_clicked.emit(to_emit)
                    )
                    # Store the stroke plotter object, which will be used later.
                    self.plot_data.plotted_strokes.append(plotted_stroke)

                    # Now that we've plotted the stroke, we need to plot the
                    # linkages. We will sort out all the linkages in the strand,
                    # and then plot them one by one.
                    for linkage in strand.items.by_type(Linkage):
                        # Linkages have a .plot_points attribute that contains three
                        # points: the first point, the midpoint, and the last point.
                        coords = linkage.plot_points
                        # Round out the coordinates using Chaikin's Corner Cutting to
                        # give the appearance of a smooth curve.
                        coords = chaikins_corner_cutting(coords, refinements=9)
                        # Split the coordinates into x and z coordinate arrays for
                        # plotting with pyqtgraph.
                        x_coords = [coord[0] for coord in coords]
                        z_coords = [coord[1] for coord in coords]

                        # Create the plot data item for the linkage.
                        plotted_linkage = pg.PlotDataItem(
                            x_coords,
                            z_coords,
                            pen=pg.mkPen(  # Create a pen for the linkage
                                color=linkage.styles.color,
                                width=linkage.styles.thickness,
                            ),
                        )
                        # Make it so that the linkage itself can be clicked.
                        plotted_linkage.setCurveClickable(True)
                        # When the linkage is clicked, emit the linkage_clicked signal.
                        # This will lead to the creation of a LinkageConfig dialog when
                        # invoked.
                        plotted_linkage.sigClicked.connect(
                            lambda *args, to_emit=linkage: self.linkage_clicked.emit(
                                to_emit
                            )
                        )
                        # Store the linkage plotter object, which will be used for
                        # actually plotting the linkage later.
                        self.plot_data.plotted_linkages.append(plotted_linkage)
                else:
                    logger.warning(
                        "Strand %s has a stroke segment that has no items. Skipping "
                        "plotting",
                        strand.name,
                    )

            # Now we can add links to the plot. While the nick objects are indeed
            # stored within each strand's items, they also are stored in the Strands
            # container object. We will iterate through the nicks through
            # strands.nicks, and then plot them one by one. Note that nicks do not
            # have strokes, which simplifies the plotting process.

            # Create a brush for the nick symbols, based on the current color scheme
            # found in settings.
        nick_brush = pg.mkBrush(color=settings.colors["nicks"])
        for nick in self.plot_data.strands.nicks:
            plotted_nick = pg.PlotDataItem(
                (nick.x_coord,),  # Just one point: the nick's x coordinate
                (nick.z_coord,),  # Just one point: the nick's z coordinate
                # The same styles for all nicks...
                symbol="o",
                symbolSize=8,
                pxMode=True,  # means that symbol size doesn't change with zoom
                symbolBrush=nick_brush,
                symbolPen=None,  # No outline for the symbol
                pen=None,  # No line connecting the points
            )
            # Store the nick plotter object, which will be used for actually
            # plotting the nick later.
            self.plot_data.plotted_nicks.append(plotted_nick)
            # Create a mapping from the nick's coordinates to the nick itself,
            # so that when it is clicked, we can find the nick object.
            self.plot_data.points[(nick.x_coord, nick.z_coord)] = nick
            # Hook up the nick's onClick method to the _points_clicked method.
            plotted_nick.sigPointsClicked.connect(self._points_clicked)

        # Items will be plotted one layer at a time, from bottom to top. The items
        # plotted last go on top, since all items before them are plotted first.
        # Thence, this list is in reverse order of the layers in the plot.
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

        # Style the plot; automatically adds labels, ticks, etc.
        self._prettify()
