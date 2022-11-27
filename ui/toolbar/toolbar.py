from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QToolBar, QWidget, QSizePolicy, QLineEdit

import settings
from ui.toolbar.actions import Actions


class Toolbar(QToolBar):
    def __init__(self, parent):
        super().__init__(parent)

        self.actions = Actions()
        for button in self.actions.buttons.values():
            self.addWidget(button)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.addWidget(spacer)

        program_label = QLineEdit(f"{settings.name} {settings.version}")
        program_label.setEnabled(False)
        program_label.setStyleSheet(
            """
        QLineEdit::disabled{
            color: rgb(0, 0, 0); 
            background-color: rgb(245, 245, 245);
        }"""
        )
        program_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        program_label.setFixedWidth(80)
        self.addWidget(program_label)

        self._prettify()

    def _prettify(self):
        self.setFloatable(False)
        self.setMovable(False)
