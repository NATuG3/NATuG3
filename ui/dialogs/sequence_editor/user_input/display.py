from PyQt6.QtCore import pyqtSignal, QMimeData
from PyQt6.QtGui import QTextCursor, QFont
from PyQt6.QtWidgets import QTextEdit

import settings
from helpers import bases_only


class DisplayArea(QTextEdit):
    updated = pyqtSignal(list)

    def __init__(self, parent, max_length=1000, fixed_length: bool = True):
        super().__init__(parent)
        self.max_length = max_length
        if fixed_length:
            self.setReadOnly(True)
        self._prettify()
        self.textChanged.connect(self.on_text_change)

    def _prettify(self):
        font = QFont("Courier New", 12)
        self.setFont(font)
        self.setStyleSheet(
            """QPlainTextEdit::disabled{
            background-color: rgb(255, 255, 255); 
            color: rgb(0, 0, 0)
            }"""
        )

    def unhighlight(self):
        """Clear any highlighted bases."""
        self.setPlainText(self.toPlainText())

    def highlight(self, index):
        """
        Highlight a specific index's character.

        Args:
            index: Character index to highlight.
        """
        html = list(self.toPlainText())
        for index_, item in enumerate(html):
            if item == " ":
                html[index_] = "&nbsp;"
        base_to_highlight = html[index]
        html[
            index
        ] = f"<span style='background-color: rgb{settings.colors['highlighted']}'>{base_to_highlight}</span>"
        html = "".join(html)
        self.setHtml(html)

    def insertFromMimeData(self, source: QMimeData) -> None:
        if len(source.text() + self.toPlainText()) > self.max_length:
            return
        self.insertPlainText(bases_only(source.text()).replace(" ", "_"))
        self.unhighlight()

    def on_text_change(self) -> None:
        new_sequence_string = bases_only(self.toPlainText())

        cursor_data = self.obtain_cursor_data()
        self.blockSignals(True)
        if self.toPlainText() != new_sequence_string:
            self.setPlainText(new_sequence_string)
        else:
            self.setPlainText(self.toPlainText())
        self.blockSignals(False)
        self.dump_cursor_data(*cursor_data)

        self.updated.emit(list(new_sequence_string))

    def obtain_cursor_data(self):
        try:
            hBar = self.horizontalScrollBar()
            hPos = hBar.value() / hBar.maximum()
        except ZeroDivisionError:
            hPos = 0
        try:
            vBar = self.verticalScrollBar()
            vPos = vBar.value() / vBar.maximum()
        except ZeroDivisionError:
            vPos = 0

        c = self.textCursor()
        p = c.position()

        return hPos, vPos, c, p

    def dump_cursor_data(self, hPos, vPos, c, p):
        c.setPosition(p)
        hBar = self.horizontalScrollBar()
        vBar = self.verticalScrollBar()
        self.setTextCursor(c)
        hBar.setValue(hPos * hBar.maximum())
        vBar.setValue(vPos * vBar.maximum())
