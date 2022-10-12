from PyQt6.QtWidgets import QSpinBox, QPushButton
from PyQt6.QtCore import Qt

from constants.directions import *
from typing import Literal
from resources.workers import fetch_icon


up_arrow, down_arrow = "↑", "↓"


class DirectionalButton(QPushButton):
    def __init__(self, parent, state: Literal[UP, DOWN]):
        super().__init__(parent)

        self.state = state

        self.setStyleSheet(
            "QPushButton{border: 2px solid rgb(220, 220, 220); border-radius: 5px; text-align: center}"
        )
        self.setFlat(True)
        self.setFixedWidth(25)
        self.text_updater()

        @self.clicked.connect
        def _(event):
            # reverse the state of the button on click
            self.state = int(not (bool(self.state)))
            # set the arrow accordingly
            self.text_updater()

    def text_updater(self):
        if self.state == UP:
            self.setIcon(fetch_icon("arrow-up-outline"))
        elif self.state == DOWN:
            self.setIcon(fetch_icon("arrow-down-outline"))


class TableIntegerBox(QSpinBox):
    """Spin box for use in QTableWidgets."""

    def __init__(self, value, show_buttons=False, ignore_scroll=True):
        """
        Initialize the integer box.

        Args:
            value (float): Initial value of the widget.
            show_buttons (bool): Show/don't show +/- buttons of integer box.
            ignore_scroll (bool): Ignore attempted scrolling to change values.
        """
        super().__init__()

        # set range from -1 to 100
        self.setMinimum(-1)
        self.setMaximum(100000)

        # set the initial value to whatever was inputted into __init__
        self.setValue(value)

        # left align interior text
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)

        # show/don't show buttons based on inputs
        if show_buttons:
            self.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
        else:
            self.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

        # if scrolling ought to be ignored then ignore it
        if ignore_scroll:
            self.wheelEvent = lambda event: event.ignore()
