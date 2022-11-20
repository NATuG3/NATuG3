from PyQt6 import uic
from PyQt6.QtWidgets import QVBoxLayout, QDialog

from ui.dialogs.sequence_editor.user_input.panel import UserInputSequenceEditor
from ui.dialogs.sequence_editor.file_input.panel import FileInputSequenceEditor


class SequenceEditor(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/dialogs/sequence_editor/sequence_editor.ui", self)

        self.manual_input.setLayout(QVBoxLayout())
        self.manual_input.layout().addWidget(UserInputSequenceEditor())

        self.file_input.setLayout(QVBoxLayout())
        self.file_input.layout().addWidget(FileInputSequenceEditor())

        self.setFixedHeight(480)
        self.setFixedWidth(700)
