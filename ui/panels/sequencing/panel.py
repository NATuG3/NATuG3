import os

from PyQt6 import uic
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QWidget, QGridLayout, QScrollArea, QFileDialog, QLineEdit

import refs
from structures.strands import Strand, Strands
from ui.dialogs.strand_config.strand_config import StrandConfig
from ui.panels.sequencing.buttons import StrandButton


class Panel(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi("ui/panels/sequencing/panel.ui", self)

        self.strand_buttons = []
        self.strands_area = QWidget()
        self.reload()

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
            filepath = QFileDialog.getSavefileName(filter=f"*.{filetype}")[0]
            self.filepath.setText(filepath)
            super(QLineEdit, self.filepath).mouseReleaseEvent(event)

        self.filepath.mouseReleaseEvent = change_filepath_clicked

        # hook the generate sequences button click event
        def export_sequences_clicked():
            """Worker for when the export sequences button is clicked."""
            filepath = self.filepath.text()[:self.filepath.text().find(".")]
            mode = self.filetype.currentText().replace(".", "")
            refs.strands.current.export(filepath, mode)

        self.export_sequences.clicked.connect(export_sequences_clicked)

    def reload(self):
        """Set up the sequencing area."""
        for button in self.strand_buttons:
            button.deleteLater()
        self.strand_buttons.clear()

        self.strands_area: QWidget
        self.strands_area.setLayout(QGridLayout())
        self.strands_area.setContentsMargins(2, 2, 2, 2)

        self.scrollable_strands_area: QScrollArea
        self.scrollable_strands_area.setContentsMargins(1, 1, 1, 1)
        self.scrollable_strands_area.setWidgetResizable(True)
        self.scrollable_strands_area.setWidget(self.strands_area)

        def strand_button_clicked(strand: Strand):
            dialog = StrandConfig(self.parent(), strand)
            dialog.show()
            dialog.updated.connect(refs.constructor.side_view.plot.refresh)
            refs.constructor.side_view.plot.refresh()

        for index, strand in enumerate(refs.strands.current.strands):
            strand_button = StrandButton(strand)
            strand_button.clicked.connect(
                lambda event, s=strand: strand_button_clicked(strand=s)
            )

            self.strands_area.layout().addWidget(strand_button)
            self.strand_buttons.append(strand_button)
