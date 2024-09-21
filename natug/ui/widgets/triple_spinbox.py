from typing import Tuple

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QSpinBox, QWidget


class TripleSpinbox(QWidget):
    editingFinished = pyqtSignal()

    def __init__(self, values: Tuple[int, int, int] = None):
        super().__init__()

        # Set the layout
        self.setLayout(QHBoxLayout())

        # Create all the spin boxes
        self.box1 = QSpinBox()
        self.box2 = QSpinBox()
        self.box3 = QSpinBox()
        self.box1.setMinimum(-99999)
        self.box2.setMinimum(-99999)
        self.box3.setMinimum(-99999)
        self.box1.setMaximum(99999)
        self.box2.setMaximum(99999)
        self.box3.setMaximum(99999)

        # Add all the spinboxes to the layout
        self.layout().addWidget(self.box1)
        self.layout().addWidget(self.box2)
        self.layout().addWidget(self.box3)

        # Set the values
        if values is not None:
            self.setValues(values)

        # Style the widget
        self._prettify()

        # Hook the signals
        self._signals()

    def _signals(self):
        """Set the styles of the spin boxes."""
        self.box1.editingFinished.connect(self.editingFinished.emit)
        self.box2.editingFinished.connect(self.editingFinished.emit)
        self.box3.editingFinished.connect(self.editingFinished.emit)

    def _prettify(self):
        """Set the styles for the widget."""
        # Set layout styles
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(1)

        # Set the button styles
        self.setFixedHeight(22)
        self.box1.setFixedSize(28, 22)
        self.box2.setFixedSize(30, 22)
        self.box3.setFixedSize(28, 22)

        self.setStyleSheet("margin:0px; padding:0px")

        # Set the button symbols
        self.box1.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.box2.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)
        self.box3.setButtonSymbols(QSpinBox.ButtonSymbols.NoButtons)

    def values(self) -> Tuple[int, int, int]:
        """Obtain a list of the values of all three buttons from left to right."""
        return self.box1.value(), self.box2.value(), self.box3.value()

    def setValues(self, values: Tuple[int, int, int]) -> None:
        """Set the values of all three spin boxes at once."""
        self.box1.setValue(values[0])
        self.box2.setValue(values[1])
        self.box3.setValue(values[2])
