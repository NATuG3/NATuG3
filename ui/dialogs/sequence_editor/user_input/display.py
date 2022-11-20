from typing import List

from PyQt6.QtCore import pyqtSignal, QMimeData
from PyQt6.QtGui import QTextCursor, QFont
from PyQt6.QtWidgets import QTextEdit

import settings
from constants.bases import DNA
from helpers import bases_only


class DisplayArea(QTextEdit):
    space = "<span style='background-color: rgb(220, 220, 220)'>&nbsp;</span>"

    def __init__(self, parent):
        super().__init__(parent)
        self._bases = []

        font = QFont("Courier New", 12)
        self.setFont(font)
        self.setReadOnly(True)
        self.setStyleSheet(
            """QPlainTextEdit::disabled{
            background-color: rgb(255, 255, 255); 
            color: rgb(0, 0, 0)
            }"""
        )

    @property
    def bases(self):
        """Obtain the current bases."""
        return self._bases

    @bases.setter
    def bases(self, bases: List[str | None]):
        """Change the displayed and stored bases."""
        self._bases = bases
        self.refresh()

    def refresh(self):
        cursor_data = self.obtain_cursor_data()
        html = ""
        for base in self.bases:
            if base in DNA:
                html += base
            elif base is None:
                html += self.space
            else:
                raise ValueError(f"Base {base} is not a valid base.")
        self.setHtml(html)
        self.dump_cursor_data(*cursor_data)

    def highlight(self, index):
        """
        Highlight a specific index's character.

        Args:
            index: Character index to highlight.
        """
        html = self.bases.copy()
        base_to_highlight = html[index]
        if base_to_highlight is None:
            base_to_highlight = "&nbsp;"
        html[index] = f"<span style='background-color: rgb{settings.colors['highlighted']}'>{base_to_highlight}</span>"

        for index_, base in enumerate(html):
            if (base is None) and (index_ != index):
                html[index_] = self.space
        html = "".join(html)

        self.setHtml(html)

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
