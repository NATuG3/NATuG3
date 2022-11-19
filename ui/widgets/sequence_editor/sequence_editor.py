from typing import List

from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtGui import QTextCursor
from PyQt6.QtWidgets import (
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QPlainTextEdit, QApplication,
)

import constants
from helpers import bases_only
from .display_area import DisplayArea
from .editor_area import EditorArea, BaseEntryBox

tester = ["A", "T", "G", "C", "T", "A"]


class SequenceEditor(QWidget):
    def __init__(self, base_count: int = 5):
        super().__init__()
        self.setWindowTitle("Sequence Editor")
        self.base_count = base_count

        self.setLayout(QVBoxLayout())

        self._display_area()
        self._editor_area()
        self._signals()
        self._prettify()

    def _prettify(self):
        self.setMinimumWidth(650)
        self.setFixedHeight(450)
        self.scrollable_editor_area.setFixedHeight(100)

    def _signals(self):
        def editor_area_updated(widget: BaseEntryBox | None):
            sequence = self.editor_area.bases
            sequence = "".join(sequence)
            self.display_area.blockSignals(True)
            self.display_area.setPlainText(sequence)
            self.display_area.blockSignals(False)

        self.editor_area.updated.connect(editor_area_updated)
        editor_area_updated(None)

        def editor_area_appended(index: int, base: str, widget: BaseEntryBox):
            def awaiter():
                self.scrollable_editor_area.ensureWidgetVisible(widget)
                self.scrollable_editor_area.horizontalScrollBar().value() + 25
            QTimer.singleShot(0, awaiter)
            self.scrollable_editor_area.ensureWidgetVisible(widget, 15, 15)

        self.editor_area.base_added.connect(editor_area_appended)

        def display_area_edited(new_bases: List[str]):
            self.editor_area.bases = new_bases

        self.display_area.updated.connect(display_area_edited)

        def editor_area_selection_changed(index: int, widget: BaseEntryBox):
            def awaiter():
                self.display_area.blockSignals(True)
                self.display_area.highlight(index)
                self.display_area.blockSignals(False)
            QTimer.singleShot(1, awaiter)

        self.editor_area.selection_changed.connect(editor_area_selection_changed)

    def _editor_area(self):
        """Create the base editor area."""
        self.editor_area = EditorArea(self, tester)

        self.scrollable_editor_area = QScrollArea()
        self.scrollable_editor_area.setWidget(self.editor_area)
        self.scrollable_editor_area.setWidgetResizable(True)
        self.scrollable_editor_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scrollable_editor_area.setStyleSheet(
            """
            QScrollArea{
                border: 1px solid rgb(170, 170, 170);
            }
        """
        )

        self.layout().addWidget(self.scrollable_editor_area)

    def _display_area(self):
        """Create the sequence viewer area."""
        self.display_area = DisplayArea(self)
        self.layout().addWidget(self.display_area)
