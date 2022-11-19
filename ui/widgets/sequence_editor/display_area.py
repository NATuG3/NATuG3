from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QTextCursor, QFont
from PyQt6.QtWidgets import QTextEdit

import constants
import settings


class DisplayArea(QTextEdit):
    updated = pyqtSignal(list)

    def __init__(self, parent):
        super().__init__(parent)
        self._prettify()
        self._signals()

    def _prettify(self):
        font = QFont("Courier New", 12)
        self.setFont(font)
        self.setStyleSheet(
            """QPlainTextEdit::disabled{
            background-color: rgb(255, 255, 255); 
            color: rgb(0, 0, 0)
            }"""
        )

    def _signals(self):
        self.textChanged.connect(self.on_text_change)

    def cursor_to_end(self):
        while self.textCursor().position() < len(self.toPlainText()):
            self.moveCursor(
                QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor
            )

    def highlight(self, index):
        """
        Highlight a specific index's character.

        Args:
            index: Character index to highlight.
        """
        html = list(self.toPlainText())
        html[index] = f"<span style='background-color: rgb{settings.colors['highlighted']}'>{html[index]}</span>"
        html = "".join(html)
        self.setHtml(html)

    def move_cursor(self, position, move_mode=QTextCursor.MoveMode.MoveAnchor):
        while position >= self.textCursor().position():
            self.moveCursor(QTextCursor.MoveOperation.Right, move_mode)
        while position < self.textCursor().position():
            self.moveCursor(QTextCursor.MoveOperation.Left, move_mode)

    def on_text_change(self) -> None:
        new_bases = []
        for potential_base in list(self.toPlainText()):
            if potential_base.upper() in constants.bases.DNA:
                new_bases.append(potential_base.upper())

        new_sequence_string = "".join(new_bases)
        if self.toPlainText() != new_sequence_string:
            previous_cursor_position = self.textCursor().position()

            self.blockSignals(True)
            self.setPlainText("".join(new_bases))
            self.blockSignals(False)

            self.move_cursor(previous_cursor_position - 1)

        self.updated.emit(new_bases)
