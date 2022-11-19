from PyQt6 import uic
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from ui.widgets.sequence_editor.user_input.panel import UserInputSequenceEditor
from ui.widgets.sequence_editor.file_input.panel import FileInputSequenceEditor


class SequenceEditor(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/widgets/sequence_editor/sequence_editor.ui", self)

        self.manual_input.setLayout(QVBoxLayout())
        self.manual_input.layout().addWidget(UserInputSequenceEditor())

        self.file_input.setLayout(QVBoxLayout())
        self.file_input.layout().addWidget(FileInputSequenceEditor())

        self.setMinimumHeight(450)
        self.setMinimumWidth(700)
