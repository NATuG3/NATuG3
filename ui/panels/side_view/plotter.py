import atexit
import logging
from copy import copy
from math import ceil, dist
from typing import List

import pyqtgraph as pg
from PyQt6 import uic
from PyQt6.QtGui import (
    QPen,
)
from PyQt6.QtWidgets import QDialog

import refs
import settings
from constants.directions import *
from constants.modes import *
from structures.points import NEMid
from structures.points.nick import Nick
from structures.strands.strand import Strand

logger = logging.getLogger(__name__)


class Plotter(pg.PlotWidget):
    """The refs plot widget for the Plotter"""

    def __init__(self):
        """Initialize plotter instance."""
        super().__init__()
        self.plot_items = []
        self._width = lambda: refs.strands.current.size[0]
        self._height = lambda: refs.strands.current.size[1]

        self.disableAutoRange()
        self._plot()
        self.autoRange()
        self.setXRange(0, self._width())
        self._prettify()

        # set up styling
        self.setWindowTitle("Side View of DNA")  # set the window's title

    def clear(self):
        for plot_item in self.plot_items:
            self.removeItem(plot_item)

    def refresh(self):
        self.clear()
        self._plot()
        logger.info("Refreshed side view.")

    def point_clicked(self, event, points):
        """Called when a point on a strand is clicked."""
        point = points[0]
        located = []
        for strand in refs.strands.current.strands:
            for item in strand.items:
                if dist(point.pos(), item.position()) < settings.junction_threshold:
                    located.append(item)
        for item in located:
            if item.pseudo:
                located.remove(item)

        refresh = refs.constructor.side_view.refresh

        if refs.mode.current == INFORMER:
            dialogs = []

            for item in located:
                item.highlighted = True

                if isinstance(item, NEMid):
                    dialog = QDialog(refs.constructor)
                    dialog.setWindowTitle("NEMid Information")
                    uic.loadUi("ui/panels/side_view/informers/NEMid.ui", dialog)
                    dialog.x_coordinate.setText(f"{item.x_coord:.4f} nanometers")
                    dialog.z_coordinate.setText(f"{item.z_coord:.4f} nanometers")
                    dialog.angle.setText(f"{item.angle:.4f}°")

                    strand_index = refs.strands.current.strands.index(item.strand)
                    openness = None
                    if item.strand.closed:
                        openness = "closed"
                    else:  # not item.strand.closed
                        openness = "open"
                    dialog.strand.setText(
                        f"item #{item.index} in {openness} strand #{strand_index}"
                    )

                    dialog.original_domain.setText(
                        f"domain #{item.domain.index + 1} of {refs.domains.current.count} domains"
                    )

                    if item.direction == UP:
                        dialog.up.setChecked(True)
                    elif item.direction == DOWN:
                        dialog.down.setChecked(True)

                    dialog.junctable.setChecked(item.junctable)
                    dialog.junction.setChecked(item.junction)

                    dialogs.append(dialog)

            def dialog_complete():
                for dialog in dialogs:
                    dialog.close()
                for item in located:
                    item.highlighted = False
                refresh()

            for dialog in dialogs:
                dialog.finished.connect(dialog_complete)
                dialog.show()
            atexit.register(dialog_complete)

            refresh()

        if refs.mode.current == JUNCTER:
            if len(located) == 2:
                if all([isinstance(item, NEMid) for item in located]):
                    refs.strands.current.add_junction(located[0], located[1])
                    refresh()
        elif refs.mode.current == NICKER:
            for item in located:
                if refs.mode.current == NICKER:
                    if isinstance(item, NEMid):
                        Nick.to_nick(item)
                    elif isinstance(item, Nick):
                        strand = item.prior.strand
                        strand.items[strand.items.index(item)] = item.prior
            refresh()

    def _prettify(self):
        # create pen for custom grid
        grid_pen: QPen = pg.mkPen(color=settings.colors["grid_lines"], width=1.4)

        # domain index grid
        for i in range(ceil(refs.strands.current.size[0]) + 1):
            self.addLine(x=i, pen=grid_pen)

        # for i in <number of helical twists of the tallest domain>...
        for i in range(0, ceil(self._width() / refs.nucleic_acid.current.H) + 1):
            self.addLine(y=(i * refs.nucleic_acid.current.H), pen=grid_pen)

        # add axis labels
        self.setLabel("bottom", text="Helical Domain")
        self.setLabel("left", text="Helical Twists", units="nanometers")

    def _plot(self):
        for _strand in refs.strands.current.strands:
            strand = copy(_strand)
            assert isinstance(strand, Strand)

            if strand.closed:
                strand.items.append(strand.items[0])
                strand.items[-1].pseudo = True

            symbols: List[str] = []
            symbol_sizes: List[str] = []
            x_coords: List[float] = []
            z_coords: List[float] = []

            NEMid_brush = pg.mkBrush(color=strand.color)
            nick_brush = pg.mkBrush(color=(settings.colors["nicks"]))
            brushes = []

            if not strand.interdomain:
                pen = pg.mkPen(color=strand.color, width=2)
            else:
                pen = pg.mkPen(color=(*strand.color, 150), width=15)

            for point in strand.items:
                x_coords.append(point.x_coord)
                z_coords.append(point.z_coord)

                if isinstance(point, NEMid):
                    if point.direction == UP:
                        symbols.append("t1")  # up arrow
                    elif point.direction == DOWN:
                        symbols.append("t")  # down arrow
                    else:
                        raise ValueError("point.direction is not UP or DOWN.", point)

                    if point.highlighted:
                        symbol_sizes.append(18)
                        brushes.append(pg.mkBrush(color=settings.colors["highlighted"]))
                    else:
                        symbol_sizes.append(6)
                        brushes.append(NEMid_brush)

                elif isinstance(point, Nick):
                    symbol_sizes.append(15)
                    symbols.append("o")
                    brushes.append(nick_brush)

            self.plot_items.append(
                (
                    self.plot(  # actually plot the current strand of the current domain
                        x_coords,
                        z_coords,
                        symbol=symbols,  # type of symbol (in this case up/down arrow)
                        symbolSize=symbol_sizes,  # size of arrows in px
                        pxMode=True,  # means that symbol size is in px and non-dynamic
                        symbolBrush=brushes,  # set color of points to current color
                        pen=pen,
                    )
                )
            )

            self.plot_items[-1].sigPointsClicked.connect(self.point_clicked)

        self._prettify()
