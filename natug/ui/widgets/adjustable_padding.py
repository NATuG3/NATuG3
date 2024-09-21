from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QSplitter, QVBoxLayout, QWidget


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
        self.vertical_slider = None
        self.horizontal_slider = None

        self._top_padding = top
        self._bottom_padding = bottom
        self._left_padding = left
        self._right_padding = right

        self._setup_ui()

    def change_padding(self, top=None, bottom=None, left=None, right=None) -> None:
        """
        Change the padding around the child widget.

        Args:
            top: Whether to add a dynamic padding slider to the top of the widget.
            bottom: Whether to add a dynamic padding slider to the bottom of the widget.
            left: Whether to add a dynamic padding slider to the left of the widget.
            right: Whether to add a dynamic padding slider to the right of the widget.
        """
        if top is not None:
            self._top_padding = top
        if bottom is not None:
            self._bottom_padding = bottom
        if left is not None:
            self._left_padding = left
        if right is not None:
            self._right_padding = right

        self._clear_ui()
        self._setup_ui()

    def _clear_ui(self):
        """Clear the UI."""
        self.layout().removeWidget(self.vertical_slider)

    def _setup_ui(self):
        # Create the horizontal slider, which contains the child widget and two dummy
        # QWidgets for padding.
        self.horizontal_slider = QSplitter()
        self.horizontal_slider.setOrientation(Qt.Orientation.Horizontal)
        if self._left_padding:
            self.horizontal_slider.addWidget(QWidget())
        self.horizontal_slider.addWidget(self.child)
        if self._right_padding:
            self.horizontal_slider.addWidget(QWidget())
        self.horizontal_slider.setSizes((0, 1, 0))
        self.horizontal_slider.setCollapsible(0, False)
        self.horizontal_slider.setCollapsible(1, False)
        self.horizontal_slider.setCollapsible(2, False)

        # Create the vertical slider, which contains the horizontal slider and two dummy
        # QWidgets for padding. The horizontal slider itself contains the child widget.
        self.vertical_slider = QSplitter()
        self.vertical_slider.setOrientation(Qt.Orientation.Vertical)
        if self._top_padding:
            self.vertical_slider.addWidget(QWidget())
        self.vertical_slider.addWidget(self.horizontal_slider)
        if self._bottom_padding:
            self.vertical_slider.addWidget(QWidget())
        self.vertical_slider.setSizes((0, 1, 0))

        # Set a main layout for ourself, and then add the vertical slider to it.
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.vertical_slider)
        self.vertical_slider.setCollapsible(0, False)
        self.vertical_slider.setCollapsible(1, False)
        self.vertical_slider.setCollapsible(2, False)
