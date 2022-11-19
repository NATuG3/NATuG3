from PyQt6.QtCore import pyqtSignal, QMimeData
from PyQt6.QtGui import QTextCursor, QFont
from PyQt6.QtWidgets import QTextEdit
import pyperclip

import constants
import settings
from helpers import bases_only


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

    def obtain_cursor_data(self):
        c = self.textCursor()
        p = c.position()
        a = c.anchor()

        vsb = self.verticalScrollBar()
        old_pos_ratio = vsb.value() / (vsb.maximum() or 1)
        return c, p, a, vsb, old_pos_ratio

    def dump_cursor_data(self, c, p, a, vsb, old_pos_ratio):
        c.setPosition(a)
        op = QTextCursor.NextCharacter if p > a else QTextCursor.MoveOperation.PreviousCharacter
        c.movePosition(op, QTextCursor.MoveMode.KeepAnchor, abs(p - a))
        self.setTextCursor(c)

        vsb.setValue(round(old_pos_ratio * vsb.maximum()))

    def insertFromMimeData(self, source: QMimeData) -> None:
        self.insertPlainText(bases_only(source.text()))

    def on_text_change(self) -> None:
        new_sequence_string = bases_only(self.toPlainText())

        if self.toPlainText() != new_sequence_string:

            previous_cursor_data = self.obtain_cursor_data()

            self.blockSignals(True)
            self.setPlainText(new_sequence_string)
            self.blockSignals(False)

            self.dump_cursor_data(*previous_cursor_data)

        self.updated.emit(list(new_sequence_string))
