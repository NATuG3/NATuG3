from PyQt6.QtWidgets import QWidget, QVBoxLayout
import pyqtgraph as pg
import workers.graph
import database.settings, database.domains
import logging

logger = logging.getLogger(__name__)


class side_view(QWidget):
    def __init__(self):
        super().__init__()

        # set layout of widget
        self.setLayout(QVBoxLayout())

        # obtain current settings
        settings = database.settings.current

        # obtain current domains
        domains = database.domains.current

        # create instance of dna_nanotube_tools side view generation
        side_view = workers.graph.side_view(
            domains,
            settings.Z_b,
            settings.Z_s,
            settings.theta_s,
            settings.theta_b,
            settings.theta_c,
        )
        logger.debug(side_view)

        plotted_window: pg.GraphicsLayoutWidget = (
            pg.GraphicsLayoutWidget()
        )  # create main plotting window
        plotted_window.setWindowTitle("Side View of DNA")  # set the window's title
        plotted_window.setBackground("w")  # make the background white
        main_plot: pg.plot = plotted_window.addPlot()

        # we can calculate the range at the end of generation; we don't need to continiously recalculate the range
        main_plot.disableAutoRange()

        # generate the coords
        x_coords = side_view._x_coords(settings.count)
        z_coords = side_view._z_coords(settings.count)

        for domain_index in range(side_view.domain_count):
            if domain_index % 2:  # if the domain index is an even integer
                colors: tuple = ((255, 0, 0), (0, 255, 0))  # use red and green colors
            else:  # but if it is an odd integer
                colors: tuple = (
                    (0, 0, 255),
                    (255, 255, 0),
                )  # use blue and yellow colors
            # this way it will be easy to discern between different domains
            # (every other domain will be a different color scheme)

            for strand_direction in range(2):
                if strand_direction == 0:  # 0 means up strand
                    symbol: str = "t1"  # up arrow for up strand
                    color: str = colors[
                        0
                    ]  # set the color to be the second option of current color scheme (which is "colors")
                elif strand_direction == 1:  # 1 means down strand
                    symbol: str = "t"  # down arrow for down strand
                    color: str = colors[
                        1
                    ]  # set the color to be the first option of current color scheme (which is "colors")

                # domain#i-up or domain#i-down
                title = f"domain#{domain_index}-{str(strand_direction).replace('0','up').replace('1','down')}"

                main_plot.plot(  # actually plot the current strand of the current domain
                    x_coords[domain_index][strand_direction],
                    z_coords[domain_index][strand_direction],
                    title=title,  # name of what was just plotted
                    symbol=symbol,  # type of symbol (in this case up/down arrow)
                    symbolSize=6,  # size of arrows in px
                    pxMode=True,  # means that symbol size is in px
                    symbolPen=pg.mkPen(
                        color=color
                    ),  # set color of points to current color
                    pen=pg.mkPen(
                        color=(120, 120, 120), width=1.8
                    ),  # set color of pen to current color (but darker)
                )

        main_plot.autoRange()  # reenable autorange so that it isn't zoomed out weirdly
        main_plot.setXRange(0, side_view.domain_count)

        # add the plot widget to the layout
        self.layout().addWidget(plotted_window)
