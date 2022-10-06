import logging
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from plotting.constants.strand_switches import *  # all strand switch literals


logger = logging.getLogger(__name__)


class panel(QWidget):
    """Nucleic Acid Config Tab."""

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("config/domains/panel.ui", self)
