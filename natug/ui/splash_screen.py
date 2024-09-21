from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QSplashScreen


class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__(
            QPixmap("ui/resources/splash_screen.png"),
            Qt.WindowType.WindowStaysOnTopHint,
        )
