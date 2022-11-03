import logging

import pyqtgraph as pg

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

        self.getViewBox().setDefaultPadding(padding=0.18)
        self.disableAutoRange()

        self._plot()
        self._prettify()

    def clear(self):
        for plot_item in self.plot_items:
            self.removeItem(plot_item)

    def refresh(self):
        self.clear()
        self._plot()

    def _prettify(self):
        # set correct range
        self.autoRange()

        # set axis labels
        self.setLabel("bottom", units="Nanometers")
        self.setLabel("left", units="Nanometers")

        # prevent user from interacting with the graph
        self.getViewBox().setAspectLocked(lock=True, ratio=1)

    def _plot(self):
        """Plot all the data."""
        worker = TopView(refs.domains.current, refs.nucleic_acid.current)

        self.plot(
            worker.u_coords,
            worker.v_coords,
            symbol="o",
            symbolSize=refs.nucleic_acid.current.D,
            symbolBrush=self.domain_brush,
            pxMode=False,
        )
