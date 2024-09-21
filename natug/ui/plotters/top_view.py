import logging
from dataclasses import dataclass, field
from math import cos, radians, sin
from typing import List

import pyqtgraph as pg
from PyQt6.QtCore import QTimer, pyqtSignal, pyqtSlot

from natug import settings
from natug.ui import plotters
from natug.ui.plotters.plotter import Plotter

logger = logging.getLogger(__name__)


@dataclass(slots=True, kw_only=True)
class PlotData:
    """
    Currently plotted data.

    Attributes:
        u_coords: X coords of the plotted data.
        v_coords: Y coords of the plotted data.
        rotation: Rotation of the plot. In degrees.
        plotted_domains: The plotted domains.
        plotted_stroke: The plotted stroke.
        plotted_numbers: The plotted numbers.
        plotted_buttons: The plotted buttons.
    """

    u_coords: List[float] = field(default_factory=list)
    v_coords: List[float] = field(default_factory=list)
    rotation: pg.PlotDataItem = 0
    plotted_domains: pg.PlotDataItem = None
    plotted_stroke: pg.PlotDataItem = None
    plotted_numbers: List[pg.PlotDataItem] = field(default_factory=list)
    plotted_buttons: List[pg.PlotDataItem] = field(default_factory=list)

    def coords(self, round_to=None):
        """
        Obtain a list of all the currently plotted coords as a zip of x and y coords.

        Args:
            round_to: The number of decimal places to round the coords to. If None, no
            rounding is performed.

        Returns:
            List of plotted coordinates. Each coordinate is a tuple of the form (x, y).
        """
        if round_to is None:
            return list(zip(self.u_coords, self.v_coords))
        else:
            return list(
                zip(
                    [round(coord, round_to) for coord in self.u_coords],
                    [round(coord, round_to) for coord in self.v_coords],
                )
            )


class TopViewPlotter(Plotter):
    """
    The plotter for plotting a top view of domains.

    Attributes:
        circle_radius: Radius of the plotted circles.
        rotation: Rotation of the plot. In degrees.
        domains: Domains to plot.
        title: Title of the plot. No title is shown if None.
        numbers: Whether to plot the domain numbers.
        stroke: Stroke width of the plotted stroke.
        plot_data: Currently plotted data.

    Signals:
        point_clicked(a tuple of the points that were clicked): Emitted when a point
            is clicked.
        domain_clicked(the index of the domain that was clicked): Emitted when a domain
            is clicked.
    """

    domain_clicked = pyqtSignal(int)
    button_clicked = pyqtSignal(object)
    point_clicked = pyqtSignal(tuple)

    def __init__(
        self,
        domains: "Domains",
        circle_radius: int,
        plot_buttons: bool = True,
        rotation: float = 0,
        numbers: bool = True,
        stroke: int = 5,
        padding: float = 0.15,
        title: str = "",
    ):
        """
        Initialize top view plotter instance.

        Args:
            domains: Domains to plot.
            circle_radius: Radius of a given domain.
            plot_buttons: Whether to plot the buttons. Defaults to True.
            rotation: Rotation of the plot. In degrees. Defaults to 0.
            numbers: Whether to plot the domain numbers. Defaults to True.
            stroke: Stroke width of the plotted stroke. Defaults to 5.
            padding: Padding of the plot to use when auto-ranging. Defaults to 0.15.
            title: Title of the plot. No title is shown if None. Defaults to None.
        """
        super().__init__()

        self.circle_radius = circle_radius
        self.plot_buttons = plot_buttons
        self.rotation = rotation
        self.domains = domains
        self.title = title
        self.numbers = numbers
        self.stroke = stroke
        self.padding = padding
        self.plot_data = PlotData()

        self.getViewBox().setDefaultPadding(0.18)

        self._plot()
        self._prettify()
        self.auto_range()

    def auto_range(self):
        # padding = self.circle_radius - .2
        # view_box = self.getViewBox()
        # view_box.setRange(
        #     xRange=(
        #         min(self.plot_data.u_coords) - padding,
        #         max(self.plot_data.u_coords) + padding,
        #     ),
        #     yRange=(
        #         min(self.plot_data.v_coords) - padding,
        #         max(self.plot_data.v_coords) + padding,
        #     ),
        # )
        QTimer.singleShot(0, self.getViewBox().autoRange)

    @pyqtSlot()
    def _point_clicked(self, event=None, points: List[pg.ScatterPlotItem] = None):
        """Slot for when points are clicked."""
        if points:
            point = points[0].pos()
            self.point_clicked.emit(tuple(point))

    def refresh(self):
        """Refresh the plot."""
        QTimer.singleShot(0, self._reset)
        QTimer.singleShot(0, self._plot)
        logger.info("Refreshed top view.")

    def _reset(self, plot_data=None):
        """Clear all plotted artifacts."""
        if plot_data is None:
            plot_data = self.plot_data
        self.removeItem(plot_data.plotted_domains)
        self.removeItem(plot_data.plotted_stroke)
        for number in plot_data.plotted_numbers:
            self.removeItem(number)
        for button in plot_data.plotted_buttons:
            self.removeItem(button)

    def _prettify(self):
        self.setTitle(self.title) if self.title else None

        # set correct range
        self.getViewBox().setDefaultPadding(self.padding)

        # set axis labels
        self.setLabel("bottom", units="Nanometers")
        self.setLabel("left", units="Nanometers")

        # prevent user from interacting with the graph in certain ways
        self.getViewBox().setAspectLocked(lock=True, ratio=1)

    def _plot_buttons(self, u_coords: List[float], v_coords: List[float]) -> None:
        """
        Plot the buttons.

        This plots the buttons and stores them in self.plot_data.

        Args:
            u_coords: X coords of the buttons.
            v_coords: Y coords of the buttons.
        """
        self.plot_data.plotted_buttons.clear()
        domains = self.domains.domains()
        domains_closed = self.domains.closed()

        for index, (u_coord, v_coord) in enumerate(zip(u_coords, v_coords)):
            if (not domains_closed) and (index == len(u_coords) - 1):
                break

            next_coord_index = (index + 1) % len(u_coords)
            button_u_coord = (u_coord + u_coords[next_coord_index]) / 2
            button_v_coord = (v_coord + v_coords[next_coord_index]) / 2
            current_domains = [domains[index], domains[next_coord_index]]
            button = self.plot(
                (button_u_coord,),
                (button_v_coord,),
                symbol="s",
                symbolSize=0.15 * self.circle_radius,
                symbolBrush=pg.mkBrush(settings.colors["domains"]["buttons"]),
                pxMode=False,
            )
            button.sigClicked.connect(
                lambda *args, domains=current_domains: self.button_clicked.emit(domains)
            )
            self.plot_data.plotted_buttons.append(button)

    def _plot_domains(self, u_coords: List[float], v_coords: List[float]) -> None:
        """
        Plot the domains.

        This plots the domains and stores them in self.plot_data.

        Args:
            u_coords: X coords of the domains.
            v_coords: Y coords of the domains.
        """
        self.plot_data.plotted_domains = self.plot(
            u_coords,
            v_coords,
            symbol="o",
            symbolSize=self.circle_radius,
            symbolBrush=pg.mkBrush(settings.colors["domains"]["fill"]),
            pxMode=False,
        )

    def _plot_stroke(self, u_coords: List[float], v_coords: List[float]) -> None:
        """
        Plot the stroke connecting the domain circles.

        This plots the stroke and stores it in self.plot_data.

        Args:
            u_coords: X coords of the plotted_stroke.
            v_coords: Y coords of the plotted_stroke.
        """
        self.plot_data.plotted_stroke = self.plot(
            u_coords,
            v_coords,
            pen=pg.mkPen(color=settings.colors["domains"]["pen"], width=self.stroke),
            symbol=None,
            pxMode=False,
        )

    def _plot_numbers(self, u_coords: List[float], v_coords: List[float]) -> None:
        """
        Plot the number labels for the plot.

        This plots the labels, sets up signals for when the user clicks them,
        and updates the plot data.
        """
        self.plot_data.plotted_numbers.clear()
        # We label domain#0 with the domain-count even though it's domain#0 in memory to
        # make it more human-friendly (so it doesn't start at #0)
        for counter, position in enumerate(tuple(zip(u_coords, v_coords)), start=1):
            symbol_size = self.circle_radius / 3
            symbol_size *= 1 + (0.255 * (len(str(counter)) - 1))

            # Plot the number
            text = self.plot(
                [position[0]],  # x coord
                [position[1]],  # y coord
                symbol=plotters.utils.custom_symbol(f"#{counter}"),  # symbol
                symbolBrush=pg.mkBrush(  # symbol color
                    color=settings.colors["domains"]["plotted_numbers"]
                ),
                symbolSize=symbol_size,  # symbol size
                pxMode=False,  # whether to dynamically scale the symbol
                pen=None,  # pen for interpoint lines. We are plotting just one
                # point at a time, so this can be set to None.
            )

            # Emit a domain_clicked signal when the user clicks a number, since the
            # numbers are the centers of domains and if they click the number it
            # means they also clicked the domain.
            text.sigPointsClicked.connect(
                lambda *args, index=counter: self.domain_clicked.emit(index)
            )
            # Emit a point_clicked signal when the user clicks a number too. This
            # emits the coordinates of the plotted number graphic that was clicked.
            text.sigPointsClicked.connect(self._point_clicked)

            # Add the text to the plot data.
            self.plot_data.plotted_numbers.append(text)

    def _plot(self):
        """
        Plot all the data.

        All the plotted data is stored in self.plot_data.
        """
        coords = self.domains.top_view()
        coords[0] = (
            (coords[0][0] + coords[1][0]) / 2,
            (coords[0][1] + coords[1][1]) / 2,
        )
        coords[-1] = (
            (coords[-2][0] + coords[-1][0]) / 2,
            (coords[-2][1] + coords[-1][1]) / 2,
        )
        u_coords, v_coords = coords[:, 0], coords[:, 1]

        # perform rotation if needed
        if self.rotation != 0:
            rotation = radians(self.rotation)
            for index, (u_coord, v_coord) in enumerate(zip(u_coords, v_coords)):
                u_coords[index] = u_coord * cos(rotation) - v_coord * sin(rotation)
                v_coords[index] = v_coord * cos(rotation) + u_coord * sin(rotation)

        # Plot the data
        self._plot_domains(u_coords[1:-1], v_coords[1:-1])
        if self.numbers:
            self._plot_numbers(u_coords[1:-1], v_coords[1:-1])
        self._plot_stroke(u_coords, v_coords)
        if self.plot_buttons:
            self._plot_buttons(u_coords[1:-1], v_coords[1:-1])

        # Store current plot data
        self.plot_data.u_coords = u_coords
        self.plot_data.v_coords = v_coords
        self.plot_data.rotation = self.rotation

        self._prettify()
