from collections import namedtuple
from typing import NamedTuple
from PyQt6.QtWidgets import QAbstractButton, QGroupBox, QHBoxLayout, QLabel, QSizePolicy
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtCore import QSize
from plotting.constants.strand_switches import * # all strand switch literals


class domain(QGroupBox):
    def __init__(self, state, index):
        super().__init__()

        self.setTitle(f"Domain #{index}")
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(strand_switch_chooser(state))
        self.layout().addWidget(QLabel("test"))
        self.layout().addWidget(QLabel("test2"))


class strand_switch_chooser(QAbstractButton):
    def __init__(self, state: int):
        super().__init__()

        self.state = state
        
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed))
        self._setup_switches()
        
        self.pixmap = QPixmap(self.strand_switches[state].icon)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(event.rect(), self.pixmap)

    def sizeHint(self):
        return QSize(50, 50)

    def _setup_switches(self):
        strand_switch: NamedTuple["stand_switch", [["switch", int], ["icon", QPixmap]]] = namedtuple("strand_switch", "switch icon")
        get_path = lambda name: f"resources/icons/strand_switches/{name}.svg" 
        self.strand_switches = {
            UP_TO_DOWN: strand_switch(-1, get_path("up_to_down")),
            DOWN_TO_DOWN: strand_switch(0, get_path("down_to_down")),
            UP_TO_UP: strand_switch(0, get_path("up_to_up")),
            DOWN_TO_UP: strand_switch(1, get_path("down_to_up"))
        }