from PyQt6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QStatusBar, QLabel
from PyQt6.QtCore import Qt
import ui

class central_widget(QWidget):
    def __init__(self):
        # this is an inherented class of QMainWindow
        # so we must initialize the parent qt widget
        super().__init__()

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(ui.panels.central_panel())

class main_window(QMainWindow):
    def __init__(self):
        # this is an inherented class of QMainWindow
        # so we must initialize the parent qt widget
        super().__init__()

        # utilize inhereted methods to set up the main window
        self.setWindowTitle("DNA Constructor")
        self.setCentralWidget(central_widget())

        # initilize status bar
        self._status_bar()

    def _status_bar(self):
        self.setStatusBar(QStatusBar())
        self.statusBar().setStyleSheet("background-color: rgb(220, 220, 220)")
