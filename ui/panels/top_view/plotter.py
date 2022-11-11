import logging

import pyqtgraph as pg

import helpers
import refs
from workers.top_view import TopView

logger = logging.getLogger(__name__)


class Plotter(pg.PlotWidget):
    domain_brush = pg.mkBrush(color=(90, 90, 90))

    def __init__(self):
        """
        Initialize plotter instance.

        Args:
            worker (SideView): The actual side view worker item.
        """
        super().__init__()
        self.worker = None
        self.text = []
        self.plotted = None

        self.getViewBox().setDefaultPadding(padding=0.18)
        self.disableAutoRange()

        self._plot()
        self._prettify()

    def point_clicked(self, event, points):
        point = points[0].pos()

        assert self.worker.u_coords.index(point[0]) == self.worker.v_coords.index(
            point[1]
        )

        # create the new active x-range for the plot
        range = self.worker.u_coords.index(point[0])
        range = range - 1, range + 2

        # store the previous range of the ui
        previous = refs.constructor.side_view.plot.visibleRange()

        refs.constructor.side_view.plot.setXRange(*range)
        refs.constructor.side_view.plot.setYRange(
            -1, refs.strands.current.size.height + 1
        )

        # if the new range is the same as the old range then this means
        # that the user has clicked on the button a second time and wants
        # to revert to the auto range of the side view plot
        if previous == refs.constructor.side_view.plot.visibleRange():
            refs.constructor.side_view.plot.autoRange()

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
        self.worker = TopView(refs.domains.current, refs.nucleic_acid.current)

        self.plotted = self.plot(
            self.worker.u_coords,
            self.worker.v_coords,
            symbol="o",
            symbolSize=refs.nucleic_acid.current.D,
            symbolBrush=self.domain_brush,
            pxMode=False,
        )

        for counter, position in enumerate(
            tuple(zip(self.worker.u_coords, self.worker.v_coords))[:-1]
        ):
            counter = str(counter + 1)
            symbol_size = refs.nucleic_acid.current.D / 3
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
            text.sigPointsClicked.connect(self.point_clicked)
            self.text.append(text)
