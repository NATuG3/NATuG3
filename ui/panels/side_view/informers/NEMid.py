from PyQt6 import uic
from PyQt6.QtWidgets import QDialog

import refs
from constants.directions import *
from structures.points import NEMid


class NEMidInformer(QDialog):
    def __init__(self, parent, NEMid_: NEMid):
        super().__init__(parent)

        self.setWindowTitle("NEMid Information")
        uic.loadUi("ui/panels/side_view/informers/NEMid.ui", self)

        self.x_coordinate.setText(f"{NEMid_.x_coord:.4f} nanometers")
        self.z_coordinate.setText(f"{NEMid_.z_coord:.4f} nanometers")
        self.angle.setText(f"{NEMid_.angle:.4f}°")

        strand_index = refs.strands.current.strands.profile_index(NEMid_.strand)
        if NEMid_.strand.closed:
            openness = "closed"
        else:  # not item.strand.closed
            openness = "open"

        self.strand.setText(
            f"item #{NEMid_.index} in {openness} strand #{strand_index}"
        )

        self.original_domain.setText(
            f"domain #{NEMid_.domain.index + 1} of {refs.domains.current.count} domains"
        )

        if NEMid_.direction == UP:
            self.up.setChecked(True)
        elif NEMid_.direction == DOWN:
            self.down.setChecked(True)

        self.junctable.setChecked(NEMid_.junctable)
        self.junction.setChecked(NEMid_.junction)
