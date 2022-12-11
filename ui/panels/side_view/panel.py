import atexit
import logging
from functools import partial
from typing import Tuple, List

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout

import refs
import ui.dialogs.informers
import ui.plotters
from constants.toolbar import *
from structures.points import NEMid, Nucleoside
from structures.strands import Strand
from ui.dialogs.strand_config.strand_config import StrandConfig

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
        dialog = StrandConfig(self.parent(), strand=strand)
        dialog.updated.connect(self.refresh)
        dialog.show()
        self.refresh()

        logger.info(f"Strand #{strand.parent.index(strand)} was clicked.")

    def points_clicked(self, points: List[Tuple[float, float]]) -> None:
        """slot for when a point in the plot is clicked."""
        if refs.toolbar.current == INFORMER:
            dialogs = []

            for item in points:
                if isinstance(item, NEMid):
                    dialogs.append(
                        ui.dialogs.informers.NEMidInformer(
                            self.parent(),
                            item,
                            refs.strands.current,
                            refs.domains.current,
                        )
                    )
                elif isinstance(item, Nucleoside):
                    dialogs.append(
                        ui.dialogs.informers.NucleosideInformer(
                            self.parent(),
                            item,
                            refs.strands.current,
                            refs.domains.current,
                        )
                    )
                else:
                    item.highlighted = False

            def dialog_complete(dialogs_, points_):
                for dialog_ in dialogs_:
                    dialog_.close()
                for point_ in points_:
                    point_.highlighted = False
                self.refresh()

            if len(dialogs) > 0:
                wrapped_dialog_complete = partial(dialog_complete, dialogs, points)
                for dialog in dialogs:
                    dialog.finished.connect(wrapped_dialog_complete)
                    dialog.show()
                atexit.register(wrapped_dialog_complete)

                self.refresh()

        if refs.toolbar.current == JUNCTER:
            # if exactly two overlapping points are clicked trigger the junction creation process
            if len(points) == 2:
                if all([isinstance(item, NEMid) for item in points]):
                    refs.strands.current.conjunct(points[0], points[1])
                    self.refresh()

        elif refs.toolbar.current == NICKER:
            raise NotImplementedError("Nicker is not yet implemented")
