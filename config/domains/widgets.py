from PyQt6.QtWidgets import QPushButton, QSpinBox, QStyle, QStyleOptionSpinBox
from PyQt6.QtCore import pyqtSignal

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
            if self.state == UP:
                self.state = DOWN
            elif self.state == DOWN:
                self.state = UP
            # set the arrow accordingly
            self.text_updater()

    def text_updater(self):
        if self.state == UP:
            self.setIcon(fetch_icon("arrow-up-outline"))
        elif self.state == DOWN:
            self.setIcon(fetch_icon("arrow-down-outline"))


class TableIntegerBox(QSpinBox):
    """Spin box for use in QTableWidgets."""

    up_button_clicked = pyqtSignal()
    down_button_clicked = pyqtSignal()

    def __init__(self, value, show_buttons=False, minimum=0, maximum=999):
        """
        Initialize the integer box.

        Args:
            value (float): Initial value of the widget.
            show_buttons (bool): Show/don't show +/- buttons of integer box.
            minimum (int): Minimum allowed value.
            maximum (int): Maximum allowed value.
        """
        super().__init__(value=value, minimum=minimum, maximum=maximum)

        # set range from -1 to 100
        self.setMinimum(minimum)
        self.setMaximum(maximum)

        # show/don't show buttons based on inputs
        if show_buttons:
            self.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
        else:
            self.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

    def mousePressEvent(self, event):
        # https://stackoverflow.com/a/65226649
        super().mousePressEvent(event)

        opt = QStyleOptionSpinBox()
        self.initStyleOption(opt)

        control = self.style().hitTestComplexControl(
            QStyle.ComplexControl.CC_SpinBox, opt, event.pos(), self
        )
        if control == QStyle.SubControl.SC_SpinBoxUp:
            self.up_button_clicked.emit()
        elif control == QStyle.SubControl.SC_SpinBoxDown:
            self.down_button_clicked.emit()
