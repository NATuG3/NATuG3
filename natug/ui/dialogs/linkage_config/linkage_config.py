import logging

from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QDialog
from PyQt6 import uic

from natug import utils
from natug.structures.strands.linkage import Linkage
from natug.ui.dialogs.sequence_editor.display_area import SequenceDisplayArea
from natug.ui.dialogs.sequence_editor.sequence_editor import SequenceEditor

logger = logging.getLogger(__name__)


class LinkageConfig(QDialog):
    updated = pyqtSignal()

    def __init__(self, parent, linkage: Linkage):
        super().__init__(parent)
        uic.loadUi("./ui/dialogs/linkage_config/linkage_config.ui", self)

        self.linkage = linkage
        self.linkage.styles.thickness += 5
        self.finished.connect(self.when_finished)

        self._sequencing()
        self._nucleoside_count()
        self._destroying()

    @pyqtSlot()
    def when_finished(self) -> None:
        self.linkage.styles.thickness -= 5
        self.updated.emit()

    def _nucleoside_count(self):
        self.nucleoside_count.setValue(len(self.linkage))

        @pyqtSlot()
        def nucleoside_count_changed():
            new_count = self.nucleoside_count.value()
            if new_count > len(self.linkage):
                self.linkage.generate(new_count - len(self.linkage))
            else:
                self.linkage.trim(len(self.linkage) - new_count)
            self.sequence_display.bases = self.linkage.sequence
            self.sequence_display.refresh()

        self.nucleoside_count.editingFinished.connect(nucleoside_count_changed)

    def _sequencing(self):
        """Set up the sequence area."""

        # add the strands display area
        self.sequence_display = SequenceDisplayArea(None, self.linkage.sequence)
        self.sequencing_area.layout().insertWidget(0, self.sequence_display)

        @pyqtSlot()
        def sequencing_editor_clicked():
            """Worker for when 'sequence editor' is clicked."""
            self.linkage.sequence = SequenceEditor.fetch_sequence(
                self.parent(), self.linkage.sequence, [None] * len(self.linkage)
            )
            self.sequence_display.bases = self.linkage.sequence
            self.updated.emit()

        self.sequence_editor.clicked.connect(sequencing_editor_clicked)

    def _destroying(self):
        def remove_linkage_clicked():
            if utils.confirm(
                self.parent(),
                "Linkage removal confirmation",
                "Are you sure you want to remove this linkage?",
            ):
                assert self.linkage.strand is not None, "Linkage has no strand."
                assert (
                    self.linkage.strand.strands is not None
                ), "Strand is not in a Strands container."
                self.linkage.strand.strands.unlink(self.linkage)
                self.close()
                self.updated.emit()
                logger.info("Use removed linkage through linkage dialog.")

        self.remove_linkage.clicked.connect(remove_linkage_clicked)
