import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication


class _Application(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        # self.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.RoundPreferFloor)
        self.setStyle("Fusion")
        self.setWindowIcon(QIcon("ui/resources/icon.ico"))
