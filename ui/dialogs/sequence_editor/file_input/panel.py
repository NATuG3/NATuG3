from PyQt6 import uic
from PyQt6.QtWidgets import QWidget


class FileInputSequenceEditor(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/widgets/sequence_editor/file_input/panel.ui", self)
