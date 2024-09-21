from typing import List

from PyQt6.QtCore import QEvent, Qt
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import QAbstractItemView, QApplication, QHeaderView, QTableWidget


class DomainsBaseTable(QTableWidget):
    """
    The parent table class for all tables in the domains tab.

    This table class has styles and tabbing events all set up.
    """

    def __init__(self, parent, headers: List[str]) -> None:
        super().__init__(parent)
        self.top_headers = tuple(headers)
        self._headers()
        self._prettify()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Intercept a keypress to alter tabbing."""
        if event.key() in (
            Qt.Key.Key_Tab,
            Qt.Key.Key_Backtab,
            Qt.Key.Key_Down,
            Qt.Key.Key_Up,
        ):
            # Determine the row and column to highlight
            row, column = self.currentRow(), self.currentColumn()
            if event.key() in (Qt.Key.Key_Tab, Qt.Key.Key_Down):
                row += 1
            else:
                row -= 1
            if row == self.rowCount():
                row = 0

            # Ensure that the previous widget's data is saved
            self.cellWidget(row, column).editingFinished.emit()
            self.cell_widget_updated.emit()

            # Disable signals temporarily
            self.setTabKeyNavigation(False)
            self.blockSignals(True)

            # Obtain the widget
            to_focus = self.cellWidget(row, column)

            # Create a list of key press events to send
            if to_focus is not None:
                # Change the table focus
                self.setCurrentCell(row, column)
                to_focus.setFocus()

                # Simulate a control A press
                QApplication.postEvent(
                    to_focus,
                    QKeyEvent(
                        QEvent.Type.KeyPress,
                        Qt.Key.Key_A,
                        Qt.KeyboardModifier.ControlModifier,
                    ),
                )

            # Unblock signals
            self.blockSignals(False)
            self.setTabKeyNavigation(True)
        else:
            # Otherwise use the normal keypress event
            super().keyPressEvent(event)

    def _headers(self):
        """Configure top headers of widget"""
        # Create a column for each header
        self.setColumnCount(len(self.top_headers))

        # Apply the headers
        self.setHorizontalHeaderLabels(self.top_headers)

    def _prettify(self):
        """Style the domain panel."""
        # Set the style worksheet of the panel
        self.setStyleSheet("QTableView::item{ padding: 3.25px; text-align: center }")

        # Show table grid
        self.setShowGrid(True)

        # Enable smooth scrolling
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        # Change the size of the table headers
        self.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.ResizeToContents
        )
