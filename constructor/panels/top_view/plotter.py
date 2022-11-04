import logging

import pyqtgraph
import pyqtgraph as pg

import constructor.panels.side_view
import references as refs
from constructor.panels.top_view.worker import TopView

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

        self.getViewBox().setDefaultPadding(padding=0.18)
        self.disableAutoRange()

        self._plot()
        self._prettify()

    def point_clicked(self, event, points):
        point = points[0].pos()

        assert self.worker.u_coords.index(point[0]) == self.worker.v_coords.index(point[1])
        range = self.worker.u_coords.index(point[0])

        refs.constructor.side_view.setXRange(range-1, range+2)
        refs.constructor.side_view.setYRange(0-1, refs.strands.current.size[1]+1)

    def clear(self):
        self.removeItem(self.plotted)

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

        spacing = refs.nucleic_acid.current.D/4

        for counter, position in enumerate(tuple(zip(self.worker.u_coords, self.worker.v_coords))[:-1]):
            text = pg.TextItem(str(f"#{counter+1}"), anchor=(0, 0))
            text.setPos(position[0]-spacing, position[1]+spacing)
            self.addItem(text)

        self.plotted.sigPointsClicked.connect(self.point_clicked)
