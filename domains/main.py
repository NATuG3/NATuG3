from PyQt6.QtWidgets import (
    QLabel
)
from PyQt6.QtGui import QWindow

import logging

logger = logging.getLogger(__name__)


class window(QWindow):
    """
    Domain configuration window.
    """

    def __init__(self):
        super().__init__()
