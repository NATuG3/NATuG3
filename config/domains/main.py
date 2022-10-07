import logging
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from constants.strand_switches import *  # all strand switch literals
from constants.directions import *
import config.domains.storage, config.domains.widgets


logger = logging.getLogger(__name__)


class panel(QWidget):
    """Nucleic Acid Config Tab."""

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("config/domains/panel.ui", self)

        # self.dump_domains(config.domains.storage.current)

    def dump_domains(self, domains_list):
        """Dump a list of domain objects."""
        return
        for index, domain in enumerate(domains_list):
            self.domains_area.addWidget(
                config.domains.widgets.domain(index, domain)
            )