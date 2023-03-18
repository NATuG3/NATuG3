import logging
from dataclasses import dataclass, field
from math import cos, radians, sin
from typing import List

import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal

import settings
import utils
from ui import plotters
from ui.plotters.plotter import Plotter

logger = logging.getLogger(__name__)


@dataclass(slots=True, kw_only=True)
class PlotData:
    """
    Currently plotted data.

    Attributes:
        plotted_numbers: The plotted number symbols.
        x_coords: X coords of plotted data.
        z_coords: Z coords of plotted data.
        domains: The currently plotted domain circles.
        rotation: The rotation of the plot.
    """

    x_coords: List[float] = field(default_factory=list)
    y_coords: List[float] = field(default_factory=list)
    rotation: pg.PlotDataItem = 0
    plotted_domains: pg.PlotDataItem = None
    plotted_stroke: pg.PlotDataItem = None
    plotted_numbers: List[pg.PlotDataItem] = None

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
            return list(zip(self.x_coords, self.y_coords))
        else:
            return list(
                zip(
                    [round(coord, round_to) for coord in self.x_coords],
                    [round(coord, round_to) for coord in self.y_coords],
                )
            )


class TopViewPlotter(Plotter):
    """
    The plotter for plotting a top view of domains.

    Attributes:
        circle_radius: Radius of the plotted circles.
        rotation: Rotation of the plot. In degrees.
        domains: Domains to plot.
        worker: The top view coordinate generator object.
        plot_data: Currently plotted data.

    Signals:
        point_clicked(a tuple of the points that were clicked): Emitted when a point
            is clicked.
        domain_clicked(the index of the domain that was clicked): Emitted when a domain
            is clicked.
    """

    domain_clicked = pyqtSignal(int)
    point_clicked = pyqtSignal(tuple)

    def __init__(
        self,
        domains: "Domains",
        domain_radius: int,
        rotation: float = 0,
        numbers: bool = True,
        title: str = "",
    ):
        """
        Initialize top view plotter instance.

        Args:
            worker: The top view coordinate generator object.
            domains: Domains to plot.
            domain_radius: Radius of a given domain.
            rotation: Rotation of the plot. In degrees. Defaults to 0.
            numbers: Whether to plot the domain numbers. Defaults to True.
            title: Title of the plot. No title is shown if None. Defaults to None.
        """

        super().__init__()

        self.circle_radius = domain_radius
        self.rotation = rotation
        self.domains = domains
        self.title = title
        self.numbers = numbers
        self.plot_data = PlotData()

        self.getViewBox().setDefaultPadding(padding=0.18)
        self.disableAutoRange()

        self._plot()
        self._prettify()

    def _point_clicked(self, event, points: List[pg.ScatterPlotItem]):
        """Slot for when points are clicked."""
        point = points[0].pos()
        self.point_clicked.emit(tuple(point))

    def refresh(self):
        """Refresh the plot."""
        self._reset()
        self._plot()
        logger.info("Refreshed top view.")

    def _reset(self, plot_data=None):
        """Clear plot_data from plot. Plot_data defaults to self.plot_data."""
        if plot_data is None:
            plot_data = self.plot_data
        self.removeItem(plot_data.plotted_domains)
        self.removeItem(plot_data.plotted_stroke)
        for number in plot_data.plotted_numbers:
            self.removeItem(number)

    def _prettify(self):
        self.setTitle(self.title) if self.title else None

        # set correct range
        self.autoRange()

        # set axis labels
        self.setLabel("bottom", units="Nanometers")
        self.setLabel("left", units="Nanometers")

        # prevent user from interacting with the graph in certain ways
        self.getViewBox().setAspectLocked(lock=True, ratio=1)

    def _plot(self):
        """
        Plot all the data.

        All the plotted data is stored in self.plot_data.
        """
        coords = self.domains.top_view()
        x_coords = [coord[0] for coord in coords]
        y_coords = [coord[1] for coord in coords]

        # perform rotation if needed
        if self.rotation != 0:
            rotation = radians(self.rotation)
            for index, (x_coord, z_coord) in enumerate(zip(x_coords, y_coords)):
                x_coords[index] = x_coord * cos(rotation) - z_coord * sin(rotation)
                y_coords[index] = z_coord * cos(rotation) + x_coord * sin(rotation)

        # plot the data
        self._plot_domains(x_coords, y_coords)
        if self.numbers:
            self._plot_numbers(x_coords, y_coords)
        self._plot_stroke(x_coords, y_coords)

        # store current plot data
        self.plot_data.x_coords = y_coords
        self.plot_data.y_coords = y_coords
        self.plot_data.rotation = self.rotation

        self._prettify()

    def _plot_domains(self, x_coords: List[float], y_coords: List[float]) -> None:
        """
        Plot the domains.

        This plots the domains and stores them in self.plot_data.

        Args:
            x_coords: X coords of the domains.
            y_coords: Y coords of the domains.
        """
        self.plot_data.plotted_domains = self.plot(
            x_coords,
            y_coords,
            symbol="o",
            symbolSize=self.circle_radius,
            symbolBrush=pg.mkBrush(settings.colors["domains"]["fill"]),
            pxMode=False,
        )

    def _plot_stroke(self, x_coords: List[float], y_coords: List[float]) -> None:
        """
        Plot the stroke connecting the domain circles.

        This plots the stroke and stores it in self.plot_data.

        Args:
            x_coords: X coords of the plotted_stroke.
            y_coords: Y coords of the plotted_stroke.
        """
        self.plot_data.plotted_stroke = self.plot(
            x_coords,
            y_coords,
            pen=pg.mkPen(color=settings.colors["domains"]["pen"], width=7),
            symbol=None,
            pxMode=False,
        )

    def _plot_numbers(self, x_coords: List[float], y_coords: List[float]) -> None:
        """
        Plot the number labels for the plot.

        This plots the labels, sets up signals for when the user clicks them,
        and updates the plot data.
        """
        self.plot_data.plotted_numbers = []
        for counter, position in enumerate(tuple(zip(x_coords, y_coords))[1:], start=1):
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
