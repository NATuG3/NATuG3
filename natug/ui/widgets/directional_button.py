from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QPushButton

from natug.constants.directions import *
from natug.ui.resources import fetch_icon

up_arrow, down_arrow = "↑", "↓"


class DirectionalButton(QPushButton):
    """
    A button to choose between UP or DOWN.

    The button always displays an up or down arrow, and clicking it alternates
    between the two.

    Attributes:
        state (int): The state of the button. Either UP or DOWN. 0 for UP 1 for DOWN.
        allow_both (bool): Whether to allow the button to be both up and down.
    """

    def __init__(self, parent, state: int, allow_both: bool = False):
        super().__init__(parent)

        self.state = state

        self.setStyleSheet(
            "QPushButton{"
            "border: 2px solid rgb(220, 220, 220);"
            " border-radius: 5px; text-align: center"
            "}"
        )
        self.setFlat(True)
        self.setFixedWidth(25)
        self.text_updater()

        @pyqtSlot()
        def on_click(event):
            # reverse the state of the button on click
            if self.state == UP:
                self.state = DOWN
            elif self.state == DOWN:
                if allow_both:
                    self.state = UP_DOWN
                else:
                    self.state = UP
            elif self.state == UP_DOWN:
                self.state = UP
            # set the arrow accordingly
            self.text_updater()

        self.clicked.connect(on_click)

    def text_updater(self):
        """Update the symbol currently shown on the button."""
        if self.state == UP:
            self.setIcon(fetch_icon("arrow-up-outline"))
        elif self.state == DOWN:
            self.setIcon(fetch_icon("arrow-down-outline"))
        elif self.state == UP_DOWN:
            self.setIcon(fetch_icon("arrow-up-down-outline"))
