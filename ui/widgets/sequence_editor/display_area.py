from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QTextCursor, QFont
from PyQt6.QtWidgets import QPlainTextEdit

import constants


class DisplayArea(QPlainTextEdit):
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
            self.moveCursor(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.MoveAnchor)

    def move_cursor(self, position, move_mode=QTextCursor.MoveMode.MoveAnchor):
        while position > self.textCursor().position():
            self.moveCursor(QTextCursor.MoveOperation.Right, move_mode)
        while position < self.textCursor().position():
            self.moveCursor(QTextCursor.MoveOperation.Left, move_mode)

    def make_selection(self, start, end):
        self.cursor_to_end()
        self.move_cursor(start)
        self.move_cursor(end, move_mode=QTextCursor.MoveMode.KeepAnchor)

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

            self.move_cursor(previous_cursor_position)

        self.updated.emit(new_bases)
