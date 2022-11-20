from functools import partial
from typing import List

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QWidget, QApplication

from .display import DisplayArea
from .editor import EditorArea

tester = ["A", "T", "C", "G", None, "A"]


class UserInputSequenceEditor(QWidget):
    def __init__(self, base_count: int = 5):
        super().__init__()
        self.setWindowTitle("Sequence Editor")
        self.base_count = base_count

        self.setLayout(QVBoxLayout())

        self._display_area()
        self._editor_area()
        self._signals()
        self._prettify()

        self.display_area.bases = self.editor_area.bases

    def _prettify(self):
        self.setMinimumWidth(650)
        self.setFixedHeight(400)
        self.scrollable_editor_area.setFixedHeight(100)

    def _signals(self):
        def update_display_area():
            self.display_area.blockSignals(True)
            self.display_area.bases = self.editor_area.bases
            for index, widget in enumerate(self.editor_area.widgets):
                if widget.hasFocus():
                    self.display_area.highlight(index)
                    break
            self.display_area.blockSignals(False)

        def editor_area_added(index: int, base: str):
            widget = self.editor_area.widgets[index]
            scroll_bar = self.scrollable_editor_area.horizontalScrollBar()
            QTimer.singleShot(
                0, partial(self.scrollable_editor_area.ensureWidgetVisible, widget)
            )
            QTimer.singleShot(1, partial(scroll_bar.setValue, scroll_bar.value() + 30))
            self.scrollable_editor_area.ensureWidgetVisible(widget, 0, 0)
            update_display_area()

        def editor_area_selection_changed(index: int):
            self.display_area.blockSignals(True)
            self.display_area.highlight(index)
            self.display_area.blockSignals(False)

        self.editor_area.base_added.connect(editor_area_added)
        self.editor_area.updated.connect(update_display_area)
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
        # self.display_area.setReadOnly(True)
