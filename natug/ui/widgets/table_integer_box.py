from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QWheelEvent
from PyQt6.QtWidgets import QSpinBox, QStyle, QStyleOptionSpinBox

up_arrow, down_arrow = "↑", "↓"


class TableIntegerBox(QSpinBox):
    """
    Spin box for use in QTableWidgets.

    This spin box is modified to:
        - ignore mouse wheel events
        - emit signals when the up/down buttons are clicked
    """

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
        super().__init__(minimum=minimum, maximum=maximum, value=value)

        # show/don't show buttons based on inputs
        if show_buttons:
            self.setButtonSymbols(QSpinBox.ButtonSymbols.UpDownArrows)
        else:
            self.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

    def wheelEvent(self, event: QWheelEvent) -> None:
        event.ignore()

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
