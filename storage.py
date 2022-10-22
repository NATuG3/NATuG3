import sys
from functools import cache

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

import config.domains
import config.nucleic_acid
import windows.constructor.main
from computers.side_view import SideView
from computers.top_view import TopView
from helpers import singleton


@cache
def application() -> QApplication:
    output = QApplication(sys.argv)
    output.setStyle("Fusion")
    output.setWindowIcon(QIcon("resources/icon.ico"))
    return output


application()


@singleton
class Plots:
    @property
    def side_view(self):
        return SideView(
            config.domains.storage.current.domains,
            config.nucleic_acid.storage.current.T,
            config.nucleic_acid.storage.current.B,
            config.nucleic_acid.storage.current.H,
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


@singleton
class Windows:
    def __init__(self):
        self.constructor = windows.constructor.main.Window()
        self.sequencer = None
