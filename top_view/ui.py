from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import top_view.workers
import logging
import config.properties
from temp import domains


logger = logging.getLogger(__name__)


class plot(QWidget):
    def __init__(self):
        super().__init__()

        # set layout of widget
        self.setLayout(QVBoxLayout())

        # obtain current settings
        settings = config.properties.current

        self.worker = top_view.workers.plot(
            domains, settings.diameter, settings.theta_c, settings.theta_s
        )
        self.worker.compute()
        logger.debug(self.worker)

        plotted_window: pg.GraphicsLayoutWidget = (
            pg.GraphicsLayoutWidget()
        )  # create main plotting window
        plotted_window.setBackground("w")  # make the background white

        main_plot = plotted_window.addPlot()

        main_plot.plot(
            self.worker.u_coords,
            self.worker.v_coords,
            symbol="o",
            symbolSize=self.worker.diameter,
            pxMode=False,
        )

        # increase the view box padding, since...
        # our symbols are VERY large circles and pyqtgraph calculates padding from the actual points, so the circles get cut off
        plotted_view_box = main_plot.getViewBox()
        plotted_view_box.setDefaultPadding(padding=0.18)

        # prevent user from interacting with the graph
        plotted_view_box.setAspectLocked(lock=True, ratio=1)

        # add the plot widget to the layout
        self.layout().addWidget(plotted_window)
