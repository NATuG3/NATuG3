from typing import List

from PyQt6.QtCore import pyqtSignal, QMimeData
from PyQt6.QtGui import QTextCursor, QFont
from PyQt6.QtWidgets import QTextEdit

import settings
from constants.bases import DNA


class DisplayArea(QTextEdit):
    """
    An area to display a nucleic acid base sequence.

    Attributes:
        bases: The bases displayed.
    """

    space = "<span style='background-color: rgb(220, 220, 220)'>&nbsp;</span>"

    def __init__(self, parent, bases):
        super().__init__(parent)
        self._bases = bases

        font = QFont("Courier New", 11)
        self.setFont(font)
        self.setReadOnly(True)
        self.setStyleSheet(
            """QPlainTextEdit::disabled{
            background-color: rgb(255, 255, 255); 
            color: rgb(0, 0, 0)
            }"""
        )
        self.setFixedHeight(285)

        self.refresh()

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
        html = ""
        for base in self.bases:
            if base in DNA:
                html += base
            elif base is None:
                html += self.space
            else:
                raise ValueError(f"Base {base} is not a valid base.")
        self.setHtml(html)

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
        html[
            index
        ] = f"<span style='background-color: rgb{settings.colors['highlighted']}'>{base_to_highlight}</span>"

        for index_, base in enumerate(html):
            if (base is None) and (index_ != index):
                html[index_] = self.space
        html = "".join(html)

        self.setHtml(html)
