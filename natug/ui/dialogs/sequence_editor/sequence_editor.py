from typing import Iterable

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDialog, QVBoxLayout
from PyQt6 import uic

from natug.ui.dialogs.sequence_editor.bulk_input.panel import BulkInputSequenceEditor
from natug.ui.dialogs.sequence_editor.user_input.panel import UserInputSequenceEditor


class SequenceEditor(QDialog):
    sequence_chosen = pyqtSignal(list)
    cancelled = pyqtSignal()

    def __init__(
        self, parent, sequence: Iterable[str | None], has_complements: Iterable[bool]
    ):
        """
        Sequence editor/selector dialog.

        Args:
            parent: The parent widget.
            sequence: The sequence to edit.
            has_complements: Whether each base has a complement that can be set. Must
                be the same length as sequence.
        """
        assert len(sequence) == len(has_complements)
        super().__init__(parent)
        uic.loadUi("./ui/dialogs/sequence_editor/sequence_editor.ui", self)

        self.bases = sequence

        if len(sequence) < 1000:
            self.manual_input = UserInputSequenceEditor(self, sequence, has_complements)
            self.manual_input_tab.setLayout(QVBoxLayout())
            self.manual_input_tab.layout().addWidget(self.manual_input)
        else:
            self.tab_area.removeTab(0)

        self.bulk_input = BulkInputSequenceEditor(self, sequence)
        self.bulk_input_tab.setLayout(QVBoxLayout())
        self.bulk_input_tab.layout().addWidget(self.bulk_input)

        self._prettify()
        self._signals()

    def _signals(self):
        """Setup pyqt signals."""

        def load_sequence_clicked():
            # update the sequence
            if self.manual_input_tab.isVisible():
                self.bases = self.manual_input.bases
            elif self.bulk_input_tab.isVisible():
                self.bases = self.bulk_input.bases

            # emit sequence updated signal
            self.sequence_chosen.emit(self.bases)

        self.load_sequence.clicked.connect(load_sequence_clicked)

        self.cancel.clicked.connect(self.cancelled.emit)

    def _prettify(self):
        self.setFixedHeight(510)
        self.setMinimumWidth(700)

    @classmethod
    def fetch_sequence(
        cls, parent, sequence: Iterable[str | None], has_complements: Iterable[bool]
    ):
        sequence_editor = cls(parent, sequence, has_complements)
        sequence_editor.sequence_chosen.connect(sequence_editor.close)
        sequence_editor.cancelled.connect(sequence_editor.close)

        if sequence_editor.exec():
            pass
        else:
            return sequence_editor.bases
