from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import sys


class Application(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.setStyle("Fusion")
        self.setWindowIcon(QIcon("resources/icon.ico"))
