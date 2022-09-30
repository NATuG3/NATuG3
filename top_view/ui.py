from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import top_view.computer
import logging
import config.nucleic_acid, config.domains
from contextlib import suppress


logger = logging.getLogger(__name__)


class plot(QWidget):
    def __init__(self):
        super().__init__()

        # set layout of widget
        self.setLayout(QVBoxLayout())

        # initilize the widget
        self.load()

    def load(self):
        with suppress(AttributeError):
            self.layout().removeWidget(self.graph)

        # obtain current settings
        settings = config.nucleic_acid.current

        # obtain current domains
        domains = config.domains.current

        self.worker = top_view.computer.plot(
            domains, settings.D, settings.theta_c, settings.theta_s
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
