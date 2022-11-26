import atexit
import logging
from functools import partial
from typing import Tuple, List

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QGroupBox, QVBoxLayout, QScrollArea

import refs
import settings
import ui.dialogs.informers
import ui.plotters
from constants.toolbar import *
from structures.points import NEMid
from structures.points.nick import Nick
from structures.strands import Strand
from ui.panels.strands.buttons import StrandButton

logger = logging.getLogger(__name__)


class Panel(QGroupBox):
    def __init__(self, parent) -> None:
        super().__init__(parent)

        self.setObjectName("Side View")
        self.setLayout(QVBoxLayout())
        self.setTitle("Side View of Helices")
        self.setStatusTip("A plot of the side view of all domains")

        self.plot = ui.plotters.SideViewPlotter(
            refs.strands.current, refs.nucleic_acid.current, refs.plot_mode.current
        )
        self.plot.points_clicked.connect(self.points_clicked)
        self.plot.strand_clicked.connect(self.strand_clicked)
        self.layout().addWidget(self.plot)

    def refresh(self) -> None:
        """Update the current plot."""
        self.plot.strands = refs.strands.current
        self.plot.nucleic_acid = refs.nucleic_acid.current
        self.plot.mode = refs.plot_mode.current
        self.plot.refresh()

    def strand_clicked(self, strand: Strand) -> None:
        """Slot for when a strand is clicked."""
        strand_button: StrandButton = (
            refs.constructor.config.panel.tabs.strands.strand_buttons[strand.index]
        )
        scroll_area: QScrollArea = (
            refs.constructor.config.panel.tabs.strands.scrollable_strands_area
        )
        strand_button.setStyleSheet(
            f"QPushButton{{background-color: rgb{settings.colors['highlighted']}}}"
        )
        scroll_area.ensureWidgetVisible(strand_button)
        QTimer.singleShot(1000, partial(strand_button.setStyleSheet, None))
        logger.info(f"Strand #{strand.index} was clicked.")

    def points_clicked(self, points: List[Tuple[float, float]]) -> None:
        """slot for when a point in the plot is clicked."""
        if refs.mode.current == INFORMER:
            dialogs = []

            for item in points:
                item.highlighted = True

                if isinstance(item, NEMid):
                    dialogs.append(
                        ui.dialogs.informers.NEMidInformer(
                            self.parent(),
                            item,
                            refs.strands.current,
                            refs.domains.current,
                        )
                    )

            def dialog_complete(dialogs_, points_):
                for dialog_ in dialogs_:
                    dialog_.close()
                for point_ in points_:
                    point_.highlighted = False
                self.refresh()

            wrapped_dialog_complete = partial(dialog_complete, dialogs, points)
            for dialog in dialogs:
                dialog.finished.connect(wrapped_dialog_complete)
                dialog.show()
            atexit.register(wrapped_dialog_complete)

            self.refresh()

        if refs.mode.current == JUNCTER:
            # if exactly two overlapping points are clicked trigger the junction creation process
            if len(points) == 2:
                if all([isinstance(item, NEMid) for item in points]):
                    refs.strands.current.conjunct(points[0], points[1])
                    self.refresh()

        elif refs.mode.current == NICKER:
            for item in points:
                if refs.mode.current == NICKER:
                    if isinstance(item, NEMid):
                        Nick.to_nick(item)
                    elif isinstance(item, Nick):
                        strand = item.prior.strand
                        strand.items[strand.items.index(item)] = item.prior
            self.refresh()
