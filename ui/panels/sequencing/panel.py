from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QGridLayout, QScrollArea

import refs
from structures.strands import Strand
from ui.dialogs.strand_config.strand_config import StrandConfig
from ui.panels.sequencing.buttons import StrandButton


class Panel(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi("ui/panels/sequencing/panel.ui", self)

        self.strand_buttons = []
        self.strands_area = QWidget()
        self.reload()

    def reload(self):
        """Set up the sequencing area"""
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
            strand_button.clicked.connect(lambda event, s=strand: strand_button_clicked(strand=s))

            self.strands_area.layout().addWidget(strand_button)
            self.strand_buttons.append(strand_button)
