from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtCore import QSize
from plotting.constants.strand_switches import *  # all strand switch literals

up_arrow, down_arrow = "↑", "↓"


# class directional_button(QPushButton):
#     def __init__(self)


class domain(QGroupBox):
    def __init__(self, state, index):
        super().__init__()

        self.setTitle(f"Domain #{index}")
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(QPushButton())
