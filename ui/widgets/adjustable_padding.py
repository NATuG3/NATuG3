from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QSplitter, QVBoxLayout


class AdjustablePadding(QWidget):
    """
    A container widget that allows the user to dynamically change whitespace around
    the widget with four handles.

    Implements a QSlider and two dummy QWidgets for configurable horizontal padding,
    within another QSlider and two dummy QWidgets for configurable vertical padding.
    """
    def __init__(self, parent, child, top=True, bottom=True, left=True, right=True):
        """
        Initialize the adjustable padding widget.

        Args:
            parent: The parent widget.
            child: The child widget.
        """
        super().__init__(parent)
        self.child = child
        self.child.setParent(self)

        # Create the horizontal slider, which contains the child widget and two dummy
        # QWidgets for padding.
        self.horizontal_slider = QSplitter()
        self.horizontal_slider.setOrientation(Qt.Orientation.Horizontal)
        if left:
            self.horizontal_slider.addWidget(QWidget())
        self.horizontal_slider.addWidget(self.child)
        if right:
            self.horizontal_slider.addWidget(QWidget())
        self.horizontal_slider.setSizes((0, 1, 0))

        # Create the vertical slider, which contains the horizontal slider and two dummy
        # QWidgets for padding. The horizontal slider itself contains the child widget.
        self.vertical_slider = QSplitter()
        self.vertical_slider.setOrientation(Qt.Orientation.Vertical)
        if top:
            self.vertical_slider.addWidget(QWidget())
        self.vertical_slider.addWidget(self.horizontal_slider)
        if bottom:
            self.vertical_slider.addWidget(QWidget())
        self.vertical_slider.setSizes((0, 1, 0))

        # Set a main layout for ourself, and then add the vertical slider to it.
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.vertical_slider)
