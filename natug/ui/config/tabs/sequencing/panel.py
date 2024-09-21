import logging
import os

from PyQt6.QtWidgets import QFileDialog, QLineEdit, QWidget
from PyQt6 import uic

from natug import utils

logger = logging.getLogger(__name__)


class SequencingPanel(QWidget):
    """DomainsPanel for strands."""

    def __init__(self, parent, runner):
        self.runner = runner
        super().__init__(parent)
        uic.loadUi("./ui/config/tabs/sequencing/panel.ui", self)

        self.strand_buttons = []

        self._configuration()
        self._tools()

    def _tools(self):
        """Set up the tools group box."""

        def run_bulk_operation_clicked():
            """Worker for when the run bulk operation button is clicked."""
            scope = self.scope.currentText()
            operation = self.operation.currentText()
            refresh = self.runner.window.side_view.refresh

            if operation == "Randomize":
                logger.debug("Performing randomization bulk operation.")
                if scope == "All Bases":
                    self.runner.managers.strands.current.randomize_sequences(True)
                    refresh()
                    logger.info("Randomized all bases in all strands.")
                elif scope == "Unset Bases":
                    self.runner.managers.strands.current.randomize_sequences(False)
                    refresh()
                    logger.info("Randomized all unset bases in all strands.")
            elif operation == "Clear":
                logger.debug("Performing clear bulk operation.")
                if scope == "All Bases":
                    self.runner.managers.strands.current.clear_sequences()
                    refresh()
                    logger.info("Cleared all bases in all strands.")
                elif scope == "Unset Bases":
                    utils.warning(
                        self.runner.window,
                        "Cannot Clear Bases",
                        "You cannot clear bases for all bases that have not been set!",
                    )

            self.runner.snapshot()

        self.run_bulk_operation.clicked.connect(run_bulk_operation_clicked)

    def _configuration(self):
        """Set up the configuration group box."""

        def filetype_updated():
            """Worker for when the filetype is updated."""
            self.filepath.setText(
                f"{os.getcwd()}{os.path.sep}export{self.filetype.currentText()}"
            )

        self.filetype.currentTextChanged.connect(filetype_updated)

        # set the initial filepath
        filetype_updated()

        # hook the filepath changed click event
        def change_filepath_clicked(event):
            """Worker for when the change filepath button is clicked."""
            filetype = self.filetype.currentText().replace(".", "")
            # by default open up the file explorer in the presets folder
            filepath = QFileDialog.getSaveFileName(
                self.parent(),
                "Sequence Export Location Chooser",
                f"{os.getcwd()}/saves/strands/preset",
                filter=f"*.{filetype} (Excel Spreadsheet)",
            )[0]
            if len(filepath) > 0:
                self.filepath.setText(filepath)
                super(QLineEdit, self.filepath).mouseReleaseEvent(event)

        self.filepath.mouseReleaseEvent = change_filepath_clicked

        # hook the generate sequences button click event
        def export_sequences_clicked():
            """Worker for when the export sequences button is clicked."""
            filepath = self.filepath.text()[: self.filepath.text().find(".")]
            self.runner.managers.strands.current.export_sequence(filepath)

        self.export_sequences.clicked.connect(export_sequences_clicked)
