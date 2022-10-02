from collections import namedtuple
import logging
from typing import NamedTuple
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPixmap
from plotting.constants.strand_switches import * # all strand switch literals
from config.domains.widgets import domain


logger = logging.getLogger(__name__)



class panel(QWidget):
    """Nucleic Acid Config Tab."""

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("config/domains/panel.ui", self)

        # load strand switch icons
        self._strand_switch()

        self.domains_table.addWidget(domain(UP_TO_DOWN, 1), 0, 0)

    def _strand_switch(self):
        folder = "strand_switches"

        strand_switch: NamedTuple["stand_switch", [["switch", int], ["icon", QPixmap]]] = namedtuple("strand_switch", "switch icon")

        get_path = lambda name: f"resources/icons/strand_switches/{name}.svg" 
        self.strand_switches = {
            "up_to_down": strand_switch(-1, get_path("up_to_down")),
            "down_to_down": strand_switch(0, get_path("down_to_down")),
            "up_to_up": strand_switch(0, get_path("up_to_up")),
            "down_to_up": strand_switch(1, get_path("down_to_up"))
        }