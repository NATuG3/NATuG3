import os

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QFileDialog, QLineEdit

import refs


class Panel(QWidget):
    """Panel for sequencing."""

    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi("ui/panels/sequencing/panel.ui", self)

        self.strand_buttons = []

        self._configuration()

    def _configuration(self):
        """Set up the configuration group box."""

        def filetype_updated():
            """Worker for when the filetype is updated."""
            self.filepath.setText(f"{os.getcwd()}\\export{self.filetype.currentText()}")

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
                f"{os.getcwd()}\\saves\\sequencing\\presets\\",
                filter=f"*.{filetype}",
            )[0]
            if len(filepath) > 0:
                self.filepath.setText(filepath)
                super(QLineEdit, self.filepath).mouseReleaseEvent(event)

        self.filepath.mouseReleaseEvent = change_filepath_clicked

        # hook the generate sequences button click event
        def export_sequences_clicked():
            """Worker for when the export sequences button is clicked."""
            filepath = self.filepath.text()[: self.filepath.text().find(".")]
            mode = self.filetype.currentText().replace(".", "")
            refs.strands.current.to_file(filepath, mode)

        self.export_sequences.clicked.connect(export_sequences_clicked)
