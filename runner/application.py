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
        pass
        # ctypes.windll.shcore.SetProcessDpiAwareness(True)


class Application(QApplication):
    """
    The main QApplication instance.

    Also manages program-wide keyboard shortcuts.
    """

    def __init__(self, runner: "Runner"):
        """
        Create a new instance of the Application class.

        Args:
            runner: NATuG's runner.
        """
        super().__init__(sys.argv)
        self.runner = runner

        self.setStyle("Fusion")
        self.setWindowIcon(QIcon("ui/resources/icon.ico"))

    def setup(self):
        pass
