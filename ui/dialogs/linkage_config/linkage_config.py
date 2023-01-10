from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog

from structures.strands.linkage import Linkage


class LinkageConfig(QDialog):
    updated = pyqtSignal()

    def __init__(self, parent, linkage: Linkage):
        super().__init__(parent)
        uic.loadUi("ui/dialogs/linkage_config/linkage_config.ui", self)
