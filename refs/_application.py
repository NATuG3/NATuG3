import ctypes
import platform
import sys

from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication


def make_dpi_aware():
    # https://stackoverflow.com/a/66299344
    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)


class _Application(QApplication):
    def __init__(self):
        make_dpi_aware()
        super().__init__(sys.argv)
        self.setStyle("Fusion")
        self.setWindowIcon(QIcon("ui/resources/icon.ico"))
