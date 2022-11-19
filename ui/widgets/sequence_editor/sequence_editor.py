from functools import partial

from PyQt6.QtCore import Qt, QPoint, QTimer
from PyQt6.QtWidgets import (
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QHBoxLayout,
    QGridLayout,
    QSizePolicy,
    QTextEdit,
    QPlainTextEdit,
)

from .editor_area import EditorArea, BaseEntryBox

tester = ["A", "T", "G", "C", "T", "A"]


class SequenceEditor(QWidget):
    def __init__(self, base_count: int = 5):
        super().__init__()
        self.setWindowTitle("Sequence Editor")
        self.base_count = base_count

        self.setLayout(QVBoxLayout())

        self._viewer_area()
        self._editor_area()

        self.setMinimumWidth(650)

        self._signals()

    def _signals(self):
        def editor_area_updated(widget: BaseEntryBox | None):
            sequence = self.editor_area.bases
            sequence = "".join(sequence)
            self.viewer_area.setPlainText(sequence)

            if widget is not None:
                QTimer.singleShot(
                    0, lambda: self.scrollable_editor_area.ensureWidgetVisible(widget)
                )
                QTimer.singleShot(
                    2,
                    lambda: self.scrollable_editor_area.horizontalScrollBar().setValue(
                        self.scrollable_editor_area.horizontalScrollBar().value() + 25
                    ),
                )
                self.scrollable_editor_area.ensureWidgetVisible(widget, 100, 100)

        self.editor_area.updated.connect(editor_area_updated)
        editor_area_updated(None)

    def _editor_area(self):
        """Create the base editor area."""
        self.editor_area = EditorArea(self, tester)
        self.scrollable_editor_area = QScrollArea()
        self.scrollable_editor_area.setWidget(self.editor_area)
        self.scrollable_editor_area.setWidgetResizable(True)
        self.layout().addWidget(self.scrollable_editor_area)
        self.scrollable_editor_area.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

    def _viewer_area(self):
        """Create the sequence viewer area."""
        self.viewer_area = QPlainTextEdit()
        self.viewer_area.setEnabled(False)
        self.viewer_area.setStyleSheet(
            "QPlainTextEdit::disabled{background-color: rgb(255, 255, 255); color: rgb(0, 0, 0)}"
        )
        self.layout().addWidget(self.viewer_area)
