import logging
from contextlib import suppress
from dataclasses import dataclass, field
from math import ceil
from typing import Dict, Iterable, List, Tuple, Type

import numpy as np
import pyqtgraph as pg
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QFont, QPainterPath, QPen

from natug import settings
from natug.constants.directions import WRAPS_LEFT_TO_RIGHT, WRAPS_RIGHT_TO_LEFT
from natug.structures.points import NEMid, Nucleoside
from natug.structures.points.point import Point, PointStyles
from natug.structures.profiles import NucleicAcidProfile
from natug.ui.plotters.plotter import Plotter
from natug.ui.plotters.utils import chaikins_corner_cutting, custom_symbol

logger = logging.getLogger(__name__)


def cross_screen_extension_coord(
    point: Point,
    direction: WRAPS_LEFT_TO_RIGHT | WRAPS_RIGHT_TO_LEFT,
    domain_count: int,
):
    """
    Obtain the coordinates of a cross screen extension.

    Args:
        point: The origin point of the cross-screen extension.
        direction: The direction to create the extension in. Either WRAPS_LEFT_TO_RIGHT or
            WRAPS_RIGHT_TO_LEFT
        domain_count: The number of total domains.
    """
    if direction == WRAPS_RIGHT_TO_LEFT:
        end_at = domain_count + settings.cross_screen_line_length
    else:
        end_at = -settings.cross_screen_line_length
    return (
        (
            point.x_coord,
            end_at,
        ),
        (point.z_coord, point.z_coord),
    )


@dataclass(slots=True)
class PlotModifiers:
    """
    Various modifiers for the scale of various plot aspects.

    Attributes:
        nick_mod: The multiplier for the size of nick points.
        nucleoside_mod: The multiplier for the size of nucleoside points.
        NEMid_mod: The multiplier for the size of NEMid points.
        point_outline_mod: The multiplier for the width of point outlines, with the
            exception of junctable NEMids.
        stroke_mod: The multiplier for the width of strand strokes.
        gridline_mod: The multiplier for the width of grid lines.
    """

    nick_mod: float = 1.0
    nucleoside_mod: float = 1.0
    NEMid_mod: float = 1.0
    point_outline_mod: float = 1.0
    stroke_mod: float = 1.0
    gridline_mod: float = 1.0


@dataclass(slots=True)
class PlotData:
    """
    Currently plotted data.

    Attributes:
        strands: The currently plotted strands.
        domains: The domains of the currently plotted strands.
        double_helices: The double helices underpinning the currently plotted strands.
        point_types: The currently plotted point types.
        modifiers: Various modifiers for the scale of various plot aspects.
        points: A mapping of positions of plotted_points to point objects.
        plotted_points: The points.
        plotted_nicks: The nicks.
        plotted_linkages: The linkages.
        plotted_unstable_indicators: All plotted unstable indicators.
        plotted_strokes: The strand pen line.
        plotted_gridlines: All the grid lines.
    """

    strands: "Strands" = None
    domains: "Domains" = None
    double_helices: "DoubleHelices" = None
    point_types: Tuple[Type, ...] = field(default_factory=tuple)
    modifiers: PlotModifiers = field(default_factory=PlotModifiers)
    points: Dict[Tuple[float, float], "Point"] = field(default_factory=dict)
    plotted_points: List[pg.PlotDataItem] = field(default_factory=list)
    plotted_nicks: List[pg.PlotDataItem] = field(default_factory=list)
    plotted_linkages: List[pg.PlotDataItem] = field(default_factory=list)
    plotted_unstable_indicators: List[pg.PlotDataItem] = field(default_factory=list)
    plotted_strokes: List[pg.PlotDataItem] = field(default_factory=list)
    plotted_gridlines: List[pg.PlotDataItem] = field(default_factory=list)


class SideViewPlotter(Plotter):
    """
    Side view strands plot widget.

    Attributes:
        strands: The strands to plot.
        domains: The domains to use for plotting computations, such as determining
            the width of the plot.
        nucleic_acid_profile: The nucleic acid nucleic_acid_profile of the
            strands to plot.
        plot_data: Currently plotted data.
        point_types: The types of points to plot. Options are Nucleoside and
            NEMid. If Point is passed, both Nucleoside and NEMid will be plotted.
        modifiers: Various modifiers for the scale of various plot aspects.
        show_instability: Whether to show which helix joints are unstable.
        dot_hidden_points: Whether to put small dots in place of points that would
            otherwise not be plotted.
        padding: Padding to apply around the plot during auto-ranging.
        title: The title of the plot.

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
        double_helices: "DoubleHelices",
        domains: "Domains",
        nucleic_acid_profile: NucleicAcidProfile,
        point_types: Tuple[Type, ...] = (Point,),
        modifiers: PlotModifiers = PlotModifiers(),
        title: str = "",
        padding: float = 0.025,
        dot_hidden_points: bool = True,
        show_unstable_helix_joints: bool = True,
        initial_plot: bool = True,
    ) -> None:
        """
        Initialize plotter instance.

        Args:
            strands: The strands to plot.
            nucleic_acid_profile: The nucleic acid nucleic_acid_profile of the
                strands to plot.
            double_helices: The double helices that the strands being plotted were derived
                from.
            domains: The domains of the strands to plot.
            point_types: The types of points to plot. Options are Nucleoside and
                NEMid. If Point is passed, both Nucleoside and NEMid will be plotted.
            modifiers: Various modifiers for the scale of various plot aspects.
            title: The title of the plot. Defaults to "".
            padding: The padding to add to the plot when auto-ranging. Defaults to 0.01.
            dot_hidden_points: Whether to show points that are not being plotted as
                small circles. Defaults to True.
            initial_plot: Whether to plot the initial data. Defaults to True.
            show_unstable_helix_joints: Whether to show which helix joints are unstable.
        """
        super().__init__()
        self.getViewBox().disableAutoRange()

        # Store initialization configurations
        self._strands = strands
        self.domains = domains
        self.double_helices = double_helices
        self.nucleic_acid_profile = nucleic_acid_profile
        self.point_types = point_types
        self.modifiers = modifiers
        self.title = title
        self.dot_hidden_points = dot_hidden_points
        self.padding = padding
        self.plot_data = PlotData()
        self.show_unstable_joints = show_unstable_helix_joints

        # Set up slots for dimensions
        self._x_min = 0
        self._x_max = 0
        self._y_min = 0
        self._y_max = 0

        # Misc. internal variables
        self._updating_viewbox = False

        # Plot data if requested
        if initial_plot:
            self.plot()
            self._set_dimensions()
            self.auto_range()

        def enableAutoRange(*args, **kwargs):
            if not self._updating_viewbox:
                self._updating_viewbox = True
                self.auto_range()
                self._updating_viewbox = False

        self.getViewBox().enableAutoRange = enableAutoRange

    @property
    def strands(self):
        """The strands to plot."""
        return self._strands

    @strands.setter
    def strands(self, strands):
        """Change the current strands to plot. Automatically updates plot dimensions."""
        self._strands = strands
        logger.debug("Updating strand dimensions")
        self._set_dimensions()

    @property
    def y_min(self):
        """The minimum y value of the plot."""
        return self._y_min

    @property
    def y_max(self):
        """The maximum y value of the plot."""
        return self._y_max

    @property
    def x_min(self):
        """The minimum x value of the plot."""
        return self._x_min

    @property
    def x_max(self):
        """The maximum x value of the plot."""
        return self._x_max

    @property
    def height(self):
        """The height of the plot."""
        return self.y_max - self.y_min

    @property
    def width(self):
        """The width of the plot."""
        return self.x_max - self.x_min

    def _set_dimensions(self):
        self._x_min = self.strands.x_min()
        self._x_max = self.strands.x_max()
        self._y_min = self.strands.y_min()
        self._y_max = self.strands.y_max()

    def refresh(self):
        """Replot plot data."""

        def runner():
            self.plot()

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
        for unstable_indicator in plot_data.plotted_unstable_indicators:
            self.removeItem(unstable_indicator)
        for points in plot_data.plotted_points:
            self.removeItem(points)
        for nick in plot_data.plotted_nicks:
            self.removeItem(nick)
        for linkage in plot_data.plotted_linkages:
            self.removeItem(linkage)
        for gridline in plot_data.plotted_gridlines:
            self.removeItem(gridline)
        self.clear()

    def _points_clicked(self, event, points):
        """Called when a point on a strand is clicked."""
        position = tuple(points[0].pos())
        self.points_clicked.emit(self.plot_data.points[position])

    def auto_range(self):
        """Configure the range for the plot automatically."""
        self.getViewBox().setXRange(self.x_min, self.x_max, self.padding)
        self.getViewBox().setYRange(self.y_min, self.y_max, self.padding)

    def auto_ranged(self):
        """Return whether the plot is currently auto-ranged."""
        return (
            self.getViewBox().viewRect().left() == 0
            and self.getViewBox().viewRect().right() == self.width
            and self.getViewBox().viewRect().top() == 0
            and self.getViewBox().viewRect().bottom() == self.height
        )

    def _prettify(self):
        """Add plotted_gridlines and style the plot."""
        # Add title
        self.setTitle(self.title) if self.title else None

        # Add axis labels
        self.setLabel("bottom", text="x", units="Helical Diameters")
        self.setLabel("left", text="z", units="Nanometers")

    def _fetch_gridline_pen(self, unstable: bool = False):
        """
        Fetch the pen to use for gridlines.

        Args:
            unstable: Whether the gridline is for an unstable joint. Defaults to False.
                If True, the pen will be styled slightly differently (red, thicker).
        """
        if unstable:
            return pg.mkPen(
                color=settings.colors["grid_lines"]["unstable"],
                width=3 + self.modifiers.gridline_mod,
            )
        else:
            return pg.mkPen(
                color=settings.colors["grid_lines"]["default"],
                width=self.modifiers.gridline_mod,
            )

    def _plot_vertical_gridline(self, x: float, unstable: bool = False):
        """
        Plot a vertical gridline at a given x coord.

        Args:
            x: The x coord to plot the gridline at.
            unstable: Whether the gridline is for an unstable joint. Defaults to False.
                If True, the pen will be styled slightly differently (red, thicker).
        """
        self.plot_data.plotted_gridlines.append(
            self.addLine(
                x=x,
                pen=self._fetch_gridline_pen(unstable=unstable),
            )
        )
        self.plot_data.plotted_gridlines[-1].setZValue(-10)

    def _plot_horizontal_gridline(self, x: float):
        """
        Plot a horizontal gridline at a given y coord.

        Args:
            y: The y coord to plot the gridline at.
        """
        self.plot_data.plotted_gridlines.append(
            self.addLine(
                y=x,
                pen=self._fetch_gridline_pen(),
            )
        )
        self.plot_data.plotted_gridlines[-1].setZValue(-10)

    def _plot_gridlines(self):
        """Plot the gridlines."""
        # Remove the preexisting gridlines
        for gridline in self.plot_data.plotted_gridlines:
            self.removeItem(gridline)

        # Clear preexisting plotted_gridlines
        self.plot_data.plotted_gridlines.clear()

        for index, double_helix in enumerate(self.double_helices):
            if double_helix.right_joint_is_stable():
                self._plot_vertical_gridline(index + 1)
            else:
                self._plot_vertical_gridline(
                    index + 1, unstable=self.show_unstable_joints
                )

        # Check if the joint on the very right side of the screen is unstable by
        # looking at the first domain's left joint.
        if self.double_helices[0].left_joint_is_stable():
            self._plot_vertical_gridline(0)
        else:
            self._plot_vertical_gridline(0, unstable=self.show_unstable_joints)

        # Plot the horizontal gridlines for each helical twist
        with suppress(ZeroDivisionError):
            # For i in <number of helical twists of the tallest domain> add grid lines.
            for i in range(0, ceil(self.height / self.nucleic_acid_profile.H)):
                self._plot_horizontal_gridline(i * self.nucleic_acid_profile.H)

    def _plot_points(self):
        """
        Plot all the points that run along the strands.

        This method automatically updates plot_data.plotted_points.
        """
        for points in self.plot_data.plotted_points:
            self.removeItem(points)
        self.plot_data.plotted_points.clear()
        self.plot_data.points.clear()

        for strand_index, strand in enumerate(self.strands):
            # First plot all the points
            to_plot = strand.items.by_type(Point)

            # create containers for plotting data
            symbols = np.empty(len(to_plot), dtype=object)
            symbol_sizes = np.empty(len(to_plot), dtype=int)
            symbol_brushes = np.empty(len(to_plot), dtype=QBrush)
            symbol_pens = np.empty(len(to_plot), dtype=QPen)
            x_coords = np.empty(len(to_plot), dtype=float)
            z_coords = np.empty(len(to_plot), dtype=float)

            # Now create the proper plot data for each point one by one
            for point_index, point in enumerate(to_plot):
                # For points that are overlapping on the integrer line, they will be
                # plotted slightly differently.
                if point.x_coord % 1 == 0:
                    # If the point is on the right side of its domain (i.e. the
                    # point's domain x coord = index + 1) then we will shift it
                    # slightly to the left so that it is not obscured by the other
                    # point that is on top of it. Otherwise, we will shift it
                    # slightly to the right.
                    if (
                        # Points that are on the very left (x=0) or the very right (
                        # x=the number of domains) will not be shifted.
                        point.x_coord == 0
                        or point.x_coord == self.domains.count
                    ):
                        x_coord = point.x_coord
                    else:
                        if point.domain.index == point.x_coord:
                            x_coord = point.x_coord + settings.domain_line_point_shift
                        else:
                            x_coord = point.x_coord - settings.domain_line_point_shift
                else:
                    x_coord = point.x_coord
                z_coord = point.z_coord

                x_coords[point_index] = x_coord
                z_coords[point_index] = z_coord

                # Update the point mappings. This is a dict that allows us to map the
                # location of a given point to the point object itself.
                self.plot_data.points[(x_coord, z_coord)] = point

                # If the point type is NOT the same as the active point type, use the
                # current styles of the point. Otherwise, plot a smaller "o" shaped
                # point to indicate that the point is not the active point type,
                # but still exists.
                if not isinstance(point, self.point_types):
                    if self.dot_hidden_points:
                        symbols[point_index] = "o"
                        symbol_sizes[point_index] = 2
                        symbol_brushes[point_index] = pg.mkBrush(color=(30, 30, 30))
                        symbol_pens[point_index] = None
                else:
                    # if the symbol is a custom symbol, use the custom symbol
                    if point.styles.symbol_is_custom():
                        if point.styles.font is None:
                            symbols[point_index] = custom_symbol(
                                point.styles.symbol,
                                flip=False,
                                rotation=point.styles.rotation,
                            )
                        else:
                            symbols[point_index] = custom_symbol(
                                point.styles.symbol,
                                flip=False,
                                rotation=point.styles.rotation,
                                font=QFont(point.styles.font),
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

                    outline_width = (
                        point.styles.outline[1] * self.modifiers.point_outline_mod
                    )
                    if isinstance(point, NEMid):
                        symbol_sizes[point_index] = (
                            point.styles.size * self.modifiers.NEMid_mod
                        )
                        if point.junctable:
                            outline_width = point.styles.outline[1]
                    elif isinstance(point, Nucleoside):
                        symbol_sizes[point_index] = (
                            point.styles.size * self.modifiers.nucleoside_mod
                        )
                    else:
                        symbol_sizes[point_index] = point.styles.size
                        outline_width = point.styles.outline[1]

                    # Create a brush for the symbol, based on the point's styles.
                    symbol_brushes[point_index] = pg.mkBrush(
                        color=point.styles.fill,
                    )

                    # Create a pen for the symbol, based on the point's styles.
                    symbol_pens[point_index] = (
                        pg.mkPen(
                            color=point.styles.outline[0],
                            width=outline_width,
                        )
                        if outline_width > 0
                        else None
                    )

            # Graph the plot for the points and for the strokes separately. First we
            # will plot the points.
            plotted_points = pg.PlotDataItem(
                x_coords,
                z_coords,
                symbol=symbols,  # type of symbol (in this case up/down arrow)
                symbolSize=symbol_sizes,  # size of arrows in px
                pxMode=True,
                symbolBrush=symbol_brushes,  # set color of points to current color
                symbolPen=symbol_pens,
                pen=None,
                skipFiniteCheck=True,
                name=f"Strand#{strand_index} Points",
            )
            # When a point is clicked, invoke the _points_clicked method.
            plotted_points.sigPointsClicked.connect(self._points_clicked)
            self.plot_data.plotted_points.append(plotted_points)

        for points in self.plot_data.plotted_points:
            self.addItem(points)

    def _plot_strands(self):
        """
        Plot all the strands onto the plot.

        Plots the strands themselves, along with linkages that are parts of the strands.

        Notes:
            - This method does not plot the points that run along the strands. That is
                done by the _plot_points() method.
        """
        for linkage in self.plot_data.plotted_linkages:
            self.removeItem(linkage)
        self.plot_data.plotted_linkages.clear()

        for stroke in self.plot_data.plotted_strokes:
            self.removeItem(stroke)
        self.plot_data.plotted_strokes.clear()
        from natug.structures.strands.linkage import Linkage

        for strand_index, strand in enumerate(self.strands.strands):
            strand_with_linkage = strand.has_linkage()

            # A strand consists of items connected by a visual stroke. However,
            # linkages receive a special stroke that has a special color, style,
            # onClick method, and more. So, right now we will split all the strand
            # items into subunits of points, discluding linkages. These subunits can
            # be plotted as connected points with a single stroke each.
            stroke_segments = strand.items.by_type(Point, Linkage).split(Linkage)
            for stroke_segment_index, stroke_segment in enumerate(stroke_segments):
                # The strand will need an extra point to give the appearance of closure
                # if the strand is closed. However, if the strand has at least one linkage
                # and is closed then the linkages should hide the gap.

                # Gather an array of all the x and z coordinates of the points in
                # the stroke segment.
                if (not strand_with_linkage) and strand.closed:
                    stroke_length = len(stroke_segment) + 1
                else:
                    stroke_length = len(stroke_segment)
                x_coords = np.zeros(stroke_length, dtype=float)
                z_coords = np.zeros(stroke_length, dtype=float)

                for point_index, point in enumerate(stroke_segment):
                    x_coords[point_index] = point.x_coord
                    z_coords[point_index] = point.z_coord

                # If the strand is closed, we will be adding a pseudo point to the
                # end of the stroke segment. If the last point and the first point
                # are near in x value, then we will connect the last point to
                # the first point (connect[-1] = True). Otherwise, we will not
                # connect the last point to the first point (connect[-1] = False).
                add_connected_pseudo_point = strand.closed and (
                    abs(stroke_segment[0].domain - stroke_segment[-1].domain)
                    == self.domains.count - 1
                )

                # If the strand is closed, a pseudo point will be added to
                # the end of the stroke segment. Whether this point gets a
                # connection depends on the "add_connected_pseudo_point"
                # variable.
                if strand.closed and not strand_with_linkage:
                    # If the strand is closed, then we need to add a pseudo
                    # point to the end of the stroke segment.
                    splitter_length = len(stroke_segment) + 1
                else:
                    # If the strand is not closed, then we don't need to add a
                    # pseudo point to the end of the stroke segment.
                    splitter_length = len(stroke_segment)

                # Create an array of booleans that indicate where to break apart
                # the coordinates into separate strokes.
                splitter = np.full(splitter_length, False, dtype=bool)

                if interdomain := strand.interdomain():
                    # If the strand is interdomain, it may also be cross-screen (
                    # that is, it breaks off on one side of the screen and
                    # continues on the other). For this reason, we will create an
                    # array of booleans that indicate where to break apart the
                    # coordinates into separate strokes. We will plot multiple
                    # stroke segments separately instead of using pyqtgraph's
                    # "connect" feature, because we will later round the edges of
                    # strokes.
                    if len(self.domains) > 2:
                        for index, point in enumerate(stroke_segment[:-1]):
                            # We will be looking ahead to the next point to determine
                            # whether we have crossed the screen, so we will skip the last
                            # point and worry about it later.
                            splitter[index + 1] = (
                                abs(
                                    point.domain.index
                                    - stroke_segment[index + 1].domain.index
                                )
                                == self.domains.count - 1
                            )

                    strand.cross_screen = splitter.any()

                    # If the strand is closed then connect the last point to the
                    # first point by creating a pseudo-point at the first point's
                    # location. This will give the appearance of a closed strand.
                    if strand.closed and not strand_with_linkage:
                        splitter[-1] = add_connected_pseudo_point
                        x_coords[-1] = x_coords[0]
                        z_coords[-1] = z_coords[0]

                    # Find the indices of the split array that are nonzero.
                    split_indexes = np.nonzero(splitter)[0]

                    # Use the indices of the split array to split the x and z arrays
                    # into subarrays, which will be connected.
                    x_coords_subarrays = np.split(x_coords, split_indexes)
                    z_coords_subarrays = np.split(z_coords, split_indexes)

                # If we know that a strand is not interdomain (does not contain
                # points within different domains, however, we can skip this
                # check and connect all the points).
                else:
                    x_coords_subarrays = (x_coords,)
                    z_coords_subarrays = (z_coords,)

                def plot_stroke(
                    x_coords: Iterable[float], z_coords: Iterable[float], smooth: bool
                ):
                    """Plot a single stroke segement."""
                    if smooth:
                        # Round the subarrays' edges using Chaikin's corner
                        # cutting algorithm.
                        rounded_coords = chaikins_corner_cutting(
                            np.column_stack((x_coords, z_coords)),
                            refinements=3,
                            offset=0.3,
                        )
                        x_coords = rounded_coords[:, 0]
                        z_coords = rounded_coords[:, 1]

                    stroke_pen = pg.mkPen(
                        color=strand.styles.color.value,
                        width=(
                            strand.styles.thickness.value * self.modifiers.stroke_mod
                        ),
                    )

                    # Create the actual plot data item for the stroke segment.
                    plotted_stroke = pg.PlotDataItem(
                        x_coords,
                        z_coords,
                        pen=stroke_pen,
                        name=f"Strand#{strand_index} Stroke#"
                        f"{stroke_segment_index}/{len(stroke_segment)}",
                    )
                    # Make it so that the stroke itself can be clicked.
                    plotted_stroke.setCurveClickable(True)
                    # When the stroke is clicked, emit the strand_clicked
                    # signal. This will lead to the creation of a
                    # StrandConfig dialog.
                    plotted_stroke.sigClicked.connect(
                        lambda *args, f=strand: self.strand_clicked.emit(f)
                    )
                    # Store the stroke plotter object, which will be used later.
                    self.plot_data.plotted_strokes.append(plotted_stroke)

                for x_coords_subarray, z_coords_subarray in zip(
                    x_coords_subarrays, z_coords_subarrays
                ):
                    plot_stroke(x_coords_subarray, z_coords_subarray, interdomain)

                if strand.cross_screen:
                    for wrap in strand.wraps(self.domains.count):
                        x_coords, z_coords = cross_screen_extension_coord(
                            wrap.point, wrap.direction, self.domains.count
                        )
                        plot_stroke(x_coords, z_coords, False)

                # Now that we've plotted the stroke, we need to plot the
                # linkages. We will sort out all the linkages in the strand,
                # and then plot them one by one.
                for linkage_index, linkage in enumerate(strand.items.by_type(Linkage)):
                    # Linkages have a .plot_points attribute that contains three
                    # points: the first point, the midpoint, and the last point.
                    coords = linkage.plot_points
                    # Round out the coordinates using Chaikin's Corner Cutting to
                    # give the appearance of a smooth curve.
                    coords = chaikins_corner_cutting(coords, refinements=3)
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
                            width=linkage.styles.thickness * self.modifiers.stroke_mod,
                        ),
                        name=f"Strand#{strand_index} Linkage#{linkage_index}",
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

        for stroke in self.plot_data.plotted_strokes:
            self.addItem(stroke)

        for linkage in self.plot_data.plotted_linkages:
            self.addItem(linkage)

    def _plot_nicks(self):
        """
        Plot all the nicks of all the strands.

        Note that nicks exist outside of strands, but represent the old location of where
        a point used to be. Because of this, all the nicks are accessed via Strands.nicks,
        which dynamically keeps track of all the nicks.
        """
        for nick in self.plot_data.plotted_nicks:
            self.removeItem(nick)
        self.plot_data.plotted_nicks.clear()

        nick_brush = pg.mkBrush(color=settings.colors["nicks"])
        for nick_index, nick in enumerate(self.strands.nicks):
            if nick.x_coord % 1 == 0:
                x_coord = (
                    nick.previous_item().domain.index + settings.domain_line_point_shift
                )
            else:
                x_coord = nick.x_coord

            # Create the plot data item for the nick.
            plotted_nick = pg.PlotDataItem(
                (x_coord,),  # Just one point: the nick's x coordinate
                (nick.z_coord,),  # Just one point: the nick's z coordinate
                # The same styles for all nicks...
                symbol="o",
                symbolSize=8 * self.modifiers.nick_mod,
                pxMode=True,  # means that symbol size doesn't change with zoom
                symbolBrush=nick_brush,
                symbolPen=None,  # No outline for the symbol
                pen=None,  # No line connecting the points
                name=f"Nick#{nick_index}",
            )
            # Store the nick plotter object, which will be used for actually
            # plotting the nick later.
            self.plot_data.plotted_nicks.append(plotted_nick)
            # Create a mapping from the nick's coordinates to the nick itself,
            # so that when it is clicked, we can find the nick object.
            self.plot_data.points[(x_coord, nick.z_coord)] = nick
            # Hook up the nick's onClick method to the _points_clicked method.
            plotted_nick.sigPointsClicked.connect(self._points_clicked)

        for nick in self.plot_data.plotted_nicks:
            self.addItem(nick)

    def plot(self):
        """
        Plot the side view.

        All plotted data gets saved in the current plot_data.

        Raises:
            ValueError: If the mode is not of type "nucleoside" or "NEMid".
        """
        self.plot_data.strands = self.strands
        self.plot_data.domains = self.domains
        self.plot_data.double_helices = self.double_helices
        self.plot_data.point_types = self.point_types
        self.plot_data.modifiers = self.modifiers

        self._plot_strands()
        self._plot_points()
        self._plot_nicks()
        self._plot_gridlines()
        self._prettify()
