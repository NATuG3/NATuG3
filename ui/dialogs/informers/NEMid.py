from PyQt6 import uic
from PyQt6.QtWidgets import QDialog

from constants.directions import *
from structures.domains import Domains
from structures.points import NEMid
from structures.strands import Strands


class NEMidInformer(QDialog):
    def __init__(
        self, parent, NEMid_: NEMid, all_strands: Strands, all_domains: Domains
    ):
        super().__init__(parent)
        assert isinstance(all_strands, Strands)
        assert isinstance(all_domains, Domains)
        assert isinstance(NEMid_, NEMid)

        self.setWindowTitle("NEMid Information")
        uic.loadUi("ui/dialogs/informers/NEMid.ui", self)

        self.x_coordinate.setText(f"{NEMid_.x_coord:.4f} nanometers")
        self.z_coordinate.setText(f"{NEMid_.z_coord:.4f} nanometers")
        self.angle.setText(f"{NEMid_.angle:.4f}°")

        strand_index = all_strands.index(NEMid_.strand)
        if NEMid_.strand.closed:
            openness = "closed"
        else:  # not item.strand.closed
            openness = "open"
        self.strand.setText(
            f"item #{NEMid_.index} in {openness} strand #{strand_index}"
        )

        self.original_domain.setText(
            f"domain #{NEMid_.domain.index + 1} of {all_domains.count} domains"
        )

        if NEMid_.direction == UP:
            self.up.setChecked(True)
        elif NEMid_.direction == DOWN:
            self.down.setChecked(True)

        self.junctable.setChecked(NEMid_.junctable)
        self.junction.setChecked(NEMid_.junction)
