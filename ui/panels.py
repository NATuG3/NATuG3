from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PyQt6 import uic


class title_panel(QWidget):
    def __init__(self):
        # this is an inherented class of QWidget
        # so we must initialize the parent qt widget
        super().__init__()

        self.setLayout(QVBoxLayout())

        # add title widget
        title = QLabel("""<h1>DNA Nanotube Constructor</h1>""")
        self.layout().addWidget(title)


class config(QFrame):
    def __init__(self) -> None:
        # this is an inherented class of QWidget
        # so we must initialize the parent qt widget
        super().__init__()

        # load the widget from the ui file
        uic.loadUi("ui/config.ui", self)
        self.setMaximumWidth(177)