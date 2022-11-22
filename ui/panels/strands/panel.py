from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QGridLayout, QScrollArea

import refs
from ui.panels.strands.strand_button import StrandButton


class Panel(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        uic.loadUi("ui/panels/strands/panel.ui", self)

        self.strand_buttons = []
        self.strands_area = QWidget()
        self._strands()

    def _strands(self):
        """Set up the strands area"""
        self.strands_area: QWidget
        self.strands_area.setLayout(QGridLayout())
        self.strands_area.setContentsMargins(2, 2, 2, 2)

        self.scrollable_strands_area: QScrollArea
        self.scrollable_strands_area.setContentsMargins(1, 1, 1, 1)
        self.scrollable_strands_area.setWidgetResizable(True)
        self.scrollable_strands_area.setWidget(self.strands_area)

        for index, strand in enumerate(refs.strands.current.strands):
            strand_button = StrandButton(strand)
            self.strands_area.layout().addWidget(strand_button)
            self.strand_buttons.append(strand_button)
