import platform
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QIcon, QPalette
from PyQt6.QtWidgets import QApplication

if platform.system() == "Windows":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
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

        # Create a light color palette
        light_palette = QPalette()
        light_palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
        light_palette.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.ColorRole.Base, QColor(250, 250, 250))
        light_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(255, 255, 255))
        light_palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(255, 255, 220))
        light_palette.setColor(QPalette.ColorRole.ToolTipText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
        light_palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
        light_palette.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
        light_palette.setColor(QPalette.ColorRole.BrightText, QColor(255, 0, 0))
        light_palette.setColor(QPalette.ColorRole.Link, QColor(0, 0, 255))
        light_palette.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))
        light_palette.setColor(
            QPalette.ColorRole.HighlightedText, QColor(255, 255, 255)
        )

        # Set the light color palette
        self.setPalette(light_palette)
        self.setStyleSheet(
            "QLineEdit { color: black; }"
            "QTextEdit { color: black; }"
            "QPlainTextEdit { color: black; }"
        )

        self.setWindowIcon(QIcon("ui/resources/icon.ico"))

    def setup(self):
        pass
