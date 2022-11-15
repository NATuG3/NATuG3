import atexit
import logging
from contextlib import suppress
from copy import copy
from math import ceil, dist
from typing import List, Tuple

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
from helpers import chaikins_corner_cutting
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
            with suppress(AttributeError):
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
            # if exactly two overlapping points are clicked trigger the junction creation process
            if len(located) == 2:
                if all([isinstance(item, NEMid) for item in located]):
                    refs.strands.current.conjunct(located[0], located[1])
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
        plotted: List[Tuple[pg.PlotDataItem, pg.PlotDataItem]] = []

        for _strand in refs.strands.current.strands:
            strand = copy(_strand)
            assert isinstance(strand, Strand)

            if strand.closed:
                strand.items.append(strand.items[0])
                strand.items[-1].pseudo = True

            symbols: List[str] = []
            symbol_sizes: List[int] = []
            x_coords: List[float] = []
            z_coords: List[float] = []
            brushes = []

            NEMid_brush = pg.mkBrush(color=strand.color)
            nick_brush = pg.mkBrush(color=(settings.colors["nicks"]))

            dim_brush = []
            for pigment in strand.color:
                pigment += 230
                if pigment > 255:
                    pigment = 255
                dim_brush.append(pigment)
            dim_brush = pg.mkBrush(color=dim_brush)

            if not strand.interdomain:
                pen = pg.mkPen(color=strand.color, width=2, pxMode=False)
            else:
                pen = pg.mkPen(color=strand.color, width=9.5, pxMode=False)

            for index, item in enumerate(strand.items):
                x_coords.append(item.x_coord)
                z_coords.append(item.z_coord)

                if isinstance(item, NEMid):
                    if item.direction == UP:
                        symbols.append("t1")  # up arrow
                    elif item.direction == DOWN:
                        symbols.append("t")  # down arrow
                    else:
                        raise ValueError("item.direction is not UP or DOWN.", item)

                    if item.highlighted:
                        symbol_sizes.append(18)
                        brushes.append(pg.mkBrush(color=settings.colors["highlighted"]))
                    else:
                        if item.junctable:
                            brushes.append(dim_brush)
                            symbol_sizes.append(6)
                        else:
                            brushes.append(NEMid_brush)
                            symbol_sizes.append(6)

                elif isinstance(item, Nick):
                    symbol_sizes.append(15)
                    symbols.append("o")
                    brushes.append(nick_brush)

            # graph the points separately
            points = pg.PlotDataItem(
                x_coords,
                z_coords,
                symbol=symbols,  # type of symbol (in this case up/down arrow)
                symbolSize=symbol_sizes,  # size of arrows in px
                pxMode=True,  # means that symbol size is in px and non-dynamic
                symbolBrush=brushes,  # set color of points to current color
                pen=None,
            )

            # if this strand contains a junction then
            # round the corners of the outline for aesthetics
            if strand.interdomain:
                coords = chaikins_corner_cutting(
                    tuple(zip(x_coords, z_coords)),
                    offset=.4,
                    refinements=1
                )
                coords = chaikins_corner_cutting(
                    coords,
                    refinements=1
                )
                x_coords = [coord[0] for coord in coords]
                z_coords = [coord[1] for coord in coords]

            outline = pg.PlotDataItem(
                x_coords,
                z_coords,
                pen=pen,
            )

            plotted.append((outline, points,))

        for outline_only, points_only in plotted:
            # plot the outline
            self.addItem(outline_only)
            self.plot_items.append(outline_only)

            # plot the points
            self.addItem(points_only)
            # add trigger to points
            points_only.sigPointsClicked.connect(self.point_clicked)
            self.plot_items.append(points_only)

        self._prettify()
