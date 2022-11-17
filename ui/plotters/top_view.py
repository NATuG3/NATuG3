import logging

import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal

import helpers
import settings
from structures.domains import Domains
from workers.top_view import TopViewWorker

logger = logging.getLogger(__name__)


class TopViewPlotter(pg.PlotWidget):
    point_clicked = pyqtSignal(tuple)

    def __init__(self, worker: TopViewWorker, domains: Domains, circle_radius: int):
        """Initialize top view plotter instance."""

        super().__init__()

        assert isinstance(worker, TopViewWorker)
        assert isinstance(domains, Domains)

        self.circle_radius = circle_radius
        self.domains = domains
        self.worker = worker

        self.text = []
        self.plotted = None

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
        self.removeItem(self.plotted)
        self.removeItem(self.text)
        self.text.clear()

    def refresh(self):
        self.clear()
        self._plot()

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
        self.plotted = self.plot(
            self.worker.u_coords,
            self.worker.v_coords,
            symbol="o",
            symbolSize=self.circle_radius,
            symbolBrush=pg.mkBrush(settings.colors["domains"]),
            pxMode=False,
        )

        for counter, position in enumerate(
            tuple(zip(self.worker.u_coords, self.worker.v_coords))[1:], start=1
        ):
            counter = str(counter)
            symbol_size = self.circle_radius / 3
            symbol_size *= 1 + (0.255 * (len(counter) - 1))
            counter = f"#{counter}"

            text = self.plot(
                [position[0]],
                [position[1]],
                symbol=helpers.custom_symbol(counter),
                symbolBrush=pg.mkBrush(color=(180, 180, 180)),
                symbolSize=symbol_size,
                pxMode=False,
                pen=None,
            )
            text.sigPointsClicked.connect(self._point_clicked)
            self.text.append(text)
