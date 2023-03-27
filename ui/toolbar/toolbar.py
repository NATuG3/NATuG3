from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QToolBar,
    QWidget,
    QSizePolicy,
    QLineEdit,
    QCheckBox,
)

import settings
from ui.toolbar.actions import Actions


class Toolbar(QToolBar):
    """
    The main toolbar with the 'modes' to interact with the side view plot with.

    Also includes a label with the program name, and an "repeat" checkbox for
    repeating actions across many nucleosides.

    Attributes:
        actions: The Actions object that holds all the toolbar buttons.
        repeat: The checkbox that holds the "repeat" checkbox and indicates whether
            to repeat the action across many nucleosides.
        program_label: The label that holds the program name.
        spacer: The spacer that holds the space between the toolbar cations and the
            program label.
    """

    def __init__(self, parent):
        super().__init__(parent)

        self.actions = Actions()
        for button in self.actions.buttons.values():
            self.addWidget(button)

        self.repeat = QCheckBox("Repeat")
        self.repeat.setStyleSheet("QCheckBox{padding-left: 3px}")
        self.repeat.setChecked(False)
        self.addWidget(self.repeat)

        self.spacer = QWidget()
        self.spacer.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.addWidget(self.spacer)

        self.program_label = QLineEdit(f"{settings.name} {settings.version}")
        self.program_label.setEnabled(False)
        self.program_label.setStyleSheet(
            """
            QLineEdit::disabled{
                color: rgb(0, 0, 0); 
                background-color: rgb(245, 245, 245);
            }"""
        )
        self.program_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.program_label.setFixedWidth(80)
        self.addWidget(self.program_label)

        self._prettify()

    def _prettify(self):
        self.setFloatable(False)
        self.setMovable(False)
