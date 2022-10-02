import plotting.structures as structures
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget


# placeholder code
current = [structures.domain(9, 0)] * 14


class widget(QWidget):
    """Nucleic Acid Config Tab"""

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("config/designer/domains.ui", self)
