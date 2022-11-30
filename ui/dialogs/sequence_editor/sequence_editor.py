from typing import List

from PyQt6 import uic
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QVBoxLayout, QDialog, QWidget

from ui.dialogs.sequence_editor.file_input.panel import FileInputSequenceEditor
from ui.dialogs.sequence_editor.user_input.panel import UserInputSequenceEditor


class SequenceEditor(QDialog):
    sequence_chosen = pyqtSignal(list)
    cancelled = pyqtSignal()

    def __init__(self, parent, sequence):
        super().__init__(parent)
        uic.loadUi("ui/dialogs/sequence_editor/sequence_editor.ui", self)

        self.sequence = sequence

        self.manual_input = UserInputSequenceEditor(sequence)
        self.manual_input_tab.setLayout(QVBoxLayout())
        self.manual_input_tab.layout().addWidget(self.manual_input)

        self.file_input = QWidget()
        self.file_input_tab.setLayout(QVBoxLayout())
        self.file_input_tab.layout().addWidget(self.file_input)

        self._prettify()
        self._signals()

    def _signals(self):
        """Setup pyqt signals."""

        def load_sequence_clicked():
            # update the sequence
            if self.manual_input_tab.isVisible():
                self.sequence = self.manual_input.bases
            elif self.file_input_tab.isVisible():
                raise NotImplementedError("File input tab is not yet implemented.")

            # emit sequence updated signal
            self.sequence_chosen.emit(self.sequence)

        self.load_sequence.clicked.connect(load_sequence_clicked)

        self.cancel.clicked.connect(self.cancelled.emit)

    def _prettify(self):
        self.setFixedHeight(510)
        self.setMinimumWidth(700)

    @classmethod
    def fetch_sequence(cls, parent, sequence: List[str]):
        sequence_editor = cls(parent, sequence)
        sequence_editor.sequence_chosen.connect(sequence_editor.close)
        sequence_editor.cancelled.connect(sequence_editor.close)

        if sequence_editor.exec():
            pass
        else:
            return sequence_editor.sequence
