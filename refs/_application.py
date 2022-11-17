import ctypes
import platform
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

QApplication.setHighDpiScaleFactorRoundingPolicy(
    Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
)
if platform.system() == "Windows":
    if int(platform.release()) >= 8:
        ctypes.windll.shcore.SetProcessDpiAwareness(True)


class _Application(QApplication):
    def __init__(self):
        super().__init__(sys.argv)

        self.setStyle("Fusion")
        self.setWindowIcon(QIcon("ui/resources/icon.ico"))
