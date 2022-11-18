from PyQt6.QtWidgets import (
    QScrollArea,
    QVBoxLayout,
    QWidget,
    QHBoxLayout, QGridLayout, QSizePolicy, QTextEdit, QPlainTextEdit,
)

from .editor_area import EditorArea


tester = ["A", "T", "G", "C", "T", "A"]


class SequenceEditor(QWidget):
    def __init__(self, base_count: int = 5):
        super().__init__()
        self.base_count = base_count

        # set up main layout for sequence editor
        self.setLayout(QHBoxLayout())

        self._editor_area()
        self._viewer_area()
        self._signals()

    def _signals(self):
        self.editor_area.updated.connect(lambda: print(self.editor_area.bases))

        @self.editor_area.updated.connect
        def editor_area_updated():
            sequence = self.editor_area.bases
            sequence = "".join(sequence)
            self.viewer_area.setPlainText(sequence)

    def _editor_area(self):
        """Create the base editor area."""
        self.editor_area = EditorArea(self, tester)
        self.editor_area.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self.layout().addWidget(self.editor_area)

    def _viewer_area(self):
        """Create the sequence viewer area."""
        self.viewer_area = QPlainTextEdit()
        self.viewer_area.setEnabled(False)
        self.viewer_area.setStyleSheet(
            "QPlainTextEdit::disabled{background-color: rgb(255, 255, 255); color: rgb(0, 0, 0)}"
        )
        self.layout().addWidget(self.viewer_area)
