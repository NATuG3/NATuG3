import atexit
import logging

from PyQt6.QtWidgets import QGroupBox, QVBoxLayout

import refs
import ui.dialogs.informers
import ui.plotters
from constants.modes import *
from structures.points import NEMid
from structures.points.nick import Nick

logger = logging.getLogger(__name__)


class Panel(QGroupBox):
    def __init__(self):
        super().__init__()

        self.setObjectName("Side View")
        self.setLayout(QVBoxLayout())
        self.setTitle("Side View of Helices")
        self.setStatusTip("A plot of the side view of all domains")

        self.plot = ui.plotters.SideViewPlotter(
            refs.strands.current, refs.nucleic_acid.current
        )
        self.layout().addWidget(self.plot)
        self.plot.points_clicked.connect(self.points_clicked)

    def refresh(self):
        """Update the current plot."""
        self.plot.strands = refs.strands.current
        self.plot.nucleic_acid = refs.nucleic_acid.current
        self.plot.refresh()

    def points_clicked(self, located):
        """Signal for when a point in the plot is clicked."""
        if refs.mode.current == INFORMER:
            dialogs = []

            for item in located:
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

            def dialog_complete():
                for dialog_ in dialogs:
                    dialog_.close()
                for item_ in located:
                    item_.highlighted = False
                self.refresh()

            for dialog in dialogs:
                dialog.finished.connect(dialog_complete)
                dialog.show()
            atexit.register(dialog_complete)

            self.refresh()

        if refs.mode.current == JUNCTER:
            # if exactly two overlapping points are clicked trigger the junction creation process
            if len(located) == 2:
                if all([isinstance(item, NEMid) for item in located]):
                    refs.strands.current.conjunct(located[0], located[1])
                    self.refresh()

        elif refs.mode.current == NICKER:
            for item in located:
                if refs.mode.current == NICKER:
                    if isinstance(item, NEMid):
                        Nick.to_nick(item)
                    elif isinstance(item, Nick):
                        strand = item.prior.strand
                        strand.items[strand.items.index(item)] = item.prior
            self.refresh()
