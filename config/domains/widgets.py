from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QPushButton, QLabel
from constants.strand_switches import *  # all strand switch literals
from constants.directions import *
from config.domains.storage import domain

up_arrow, down_arrow = "↑", "↓"


class directional_button(QPushButton):
    def __init__(self, parent, state: int):
        super().__init__(parent)

        assert state in (UP, DOWN)

        if state == UP:
            self.setText("↑")
        elif state == DOWN:
            self.setText("↓")


class domain(QGroupBox):
    def __init__(self, index, domain: domain):
        super().__init__()

        self.setTitle(f"Domain #{index}")
        self.setLayout(QHBoxLayout())

        self.joints = [
            directional_button(self, domain.helix_joints[LEFT]),
            directional_button(self, domain.helix_joints[RIGHT]),
        ]

        # left joint
        self.layout().addWidget(self.joints[0])

        # right joint
        self.layout().addWidget(self.joints[1])

        self.layout().addWidget(QLabel("test"))
