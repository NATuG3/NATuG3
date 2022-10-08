from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import plotting.top_view.worker
import logging
from contextlib import suppress
import config.nucleic_acid, config.domains


logger = logging.getLogger(__name__)


class Plot(QWidget):
    def __init__(self):
        super().__init__()

        # set layout of widget
        self.setLayout(QVBoxLayout())

        # initilize the widget
        self.load()

    def load(self):
        """
        Fetch settings data and actually plot the top view graph.
        Automatically replaces existing plot if this has already been called.
        """

        # attempt to remove existing widget if it is already generated
        # (so that we don't end up with two widgets)
        with suppress(AttributeError):
            self.layout().removeWidget(self.graph)

        # fetch nucleic acid settings and the current domains
        self.settings = config.nucleic_acid.storage.current
        self.domains = config.domains.storage.current

        self.worker = plotting.top_view.worker.Plot(
            self.domains, self.settings.D, self.settings.theta_c, self.settings.theta_s
        )
        self.worker.compute()
        logger.debug(self.worker)

        self.graph: pg.GraphicsLayoutWidget = (
            pg.GraphicsLayoutWidget()
        )  # create main plotting window
        self.graph.setBackground("w")  # make the background white

        main_plot = self.graph.addPlot()

        main_plot.plot(
            self.worker.u_coords,
            self.worker.v_coords,
            symbol="o",
            symbolSize=self.worker.D,
            pxMode=False,
        )

        # increase the view box padding, since...
        # our symbols are VERY large circles and pyqtgraph calculates padding from the actual points, so the circles get cut off
        plotted_view_box = main_plot.getViewBox()
        plotted_view_box.setDefaultPadding(padding=0.18)

        # prevent user from interacting with the graph
        plotted_view_box.setAspectLocked(lock=True, ratio=1)

        # add the plot widget to the layout
        self.layout().addWidget(self.graph)
