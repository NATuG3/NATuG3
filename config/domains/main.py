import logging
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QTableWidget
from config.domains import storage


logger = logging.getLogger(__name__)


class table(QTableWidget):
    """Nucleic Acid Config Tab."""

    def __init__(self, parent) -> None:
        super().__init__()
        self.parent = parent
        print(storage.current[0])


    def dump_domains(self, domains_list):
        """Dump a list of domain objects."""
        pass


class panel(QWidget):
    """Nucleic Acid Config Tab."""

    def __init__(self) -> None:
        super().__init__()

        # load in the panel's designer UI
        uic.loadUi("config/domains/panel.ui", self)



