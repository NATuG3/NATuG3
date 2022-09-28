from PyQt6 import uic
from PyQt6.QtWidgets import QWidget


class widget(QWidget):
    """Config panel"""

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("resources/designer/config.ui", self)
