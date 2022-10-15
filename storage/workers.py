import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

import config.domains
import config.nucleic_acid
import windows.constructor.main
from computers.side_view import SideView
from computers.top_view import TopView


def application() -> QApplication:
    output = QApplication(sys.argv)
    output.setStyle("Fusion")
    output.setWindowIcon(QIcon("resources/icon.ico"))
    return output


class Plots:
    @property
    def side_view(self):
        return SideView(
            config.domains.storage.current.domains,
            config.nucleic_acid.storage.current.Z_b,
            config.nucleic_acid.storage.current.Z_s,
            config.nucleic_acid.storage.current.theta_s,
            config.nucleic_acid.storage.current.theta_b,
            config.nucleic_acid.storage.current.theta_c,
        )

    @property
    def top_view(self):
        return TopView(
            config.domains.storage.current.domains,
            config.nucleic_acid.storage.current.D,
            config.nucleic_acid.storage.current.theta_c,
            config.nucleic_acid.storage.current.theta_s,
        )


class Windows:
    def __init__(self):
        self.constructor = windows.constructor.main.Window()
        self.sequencer = None
