import logging
from dataclasses import dataclass
from math import cos, radians, sin

import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal

import helpers
import settings
from structures.domains import Domains
from workers.top_view import TopViewWorker

logger = logging.getLogger(__name__)


class TopViewPlotter(pg.PlotWidget):
    point_clicked = pyqtSignal(tuple)

    @dataclass
    class PlotData:
        numbers: list | None
        x_coords: list | None
        z_coords: list | None
        domains: list | None
        stroke: list | None
        rotation: float | None

    def __init__(
            self,
            worker: TopViewWorker,
            domains: Domains,
            domain_radius: int,
            rotation: float = 0,
    ):
        """
        Initialize top view plotter instance.

        Args:
            worker: The top view coordinate generator object.
            domains: Domains to plot.
            domain_radius: Radius of a given domain.
            rotation: Rotation of the plot. In degrees. Defaults to 0.
        """

        super().__init__()

        assert isinstance(worker, TopViewWorker)
        assert isinstance(domains, Domains)

        self.circle_radius = domain_radius
        self.rotation = rotation
        self.domains = domains
        self.worker = worker

        self.plot_data = self.PlotData(
            numbers=None,
            x_coords=None,
            z_coords=None,
            domains=None,
            stroke=None,
            rotation=self.rotation,
        )

        self.getViewBox().setDefaultPadding(padding=0.18)
        self.disableAutoRange()

        self._plot()
        self._prettify()

    def _point_clicked(self, event, points):
        point = points[0].pos()
        assert self.worker.u_coords.index(point[0]) == self.worker.v_coords.index(
            point[1]
        )
        self.point_clicked.emit(tuple(point))

    def clear(self):
        self.removeItem(self.plot_data.domains)
        self.removeItem(self.plot_data.stroke)
        self.removeItem(self.plot_data.numbers)
        self.text.clear()

    def refresh(self):
        self.clear()
        self._plot()
        logger.info("Refreshed top view.")

    def _prettify(self):
        # set correct range
        self.autoRange()

        # set axis labels
        self.setLabel("bottom", units="Nanometers")
        self.setLabel("left", units="Nanometers")

        # prevent user from interacting with the graph in certain ways
        self.getViewBox().setAspectLocked(lock=True, ratio=1)

    def _plot(self):
        """Plot all the data."""
        x_coords, z_coords = self.worker.u_coords, self.worker.v_coords

        # proform rotation if needed
        if self.rotation != 0:
            rotation = radians(self.rotation)
            for index, (x_coord, z_coord) in enumerate(zip(x_coords, z_coords)):
                x_coords[index] = x_coord * cos(rotation) - z_coord * sin(rotation)
                z_coords[index] = z_coord * cos(rotation) + x_coord * sin(rotation)

        # plot the data
        self._plot_domains(x_coords, z_coords)
        self._plot_numbers(x_coords, z_coords)
        self._plot_stroke(x_coords, z_coords)

        # store current plot data
        self.plot_data.x_coords = x_coords
        self.plot_data.z_coords = z_coords
        self.plot_data.rotation = self.rotation

    def _plot_domains(self, x_coords, y_coords):
        """Plot the domains."""
        self.circles = self.plot(
            x_coords,
            y_coords,
            symbol="o",
            symbolSize=self.circle_radius,
            symbolBrush=pg.mkBrush(settings.colors["domains"]["fill"]),
            pxMode=False,
        )

    def _plot_stroke(self, x_coords, y_coords):
        """Plot the stroke."""
        self.plotted_stroke = self.plot(
            x_coords,
            y_coords,
            pen=pg.mkPen(color=settings.colors["domains"]["pen"], width=7),
            symbol=None,
            pxMode=False,
        )

    def _plot_numbers(self, x_coords, y_coords):
        """Plot the numbers."""
        self.plotted_numbers = []
        for counter, position in enumerate(tuple(zip(x_coords, y_coords))[1:], start=1):
            counter = str(counter)
            symbol_size = self.circle_radius / 3
            symbol_size *= 1 + (0.255 * (len(counter) - 1))
            counter = f"#{counter}"

            text = self.plot(
                [position[0]],
                [position[1]],
                symbol=helpers.custom_symbol(counter),
                symbolBrush=pg.mkBrush(color=settings.colors["domains"]["numbers"]),
                symbolSize=symbol_size,
                pxMode=False,
                pen=None,
            )
            text.sigPointsClicked.connect(self._point_clicked)
            self.plotted_numbers.append(text)
