from PyQt6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QLabel, QStatusBar
import ui


class central_widget(QWidget):
    def __init__(self) -> None:
        # this is an inherented class of QWidget
        # so we must initialize the parent qt widget
        super().__init__()

        # this is the main window's central widget, which is a vertical array layout
        self.setLayout(QVBoxLayout())

        # add title/software description top panel
        self.layout().addWidget(ui.panels.title_panel())
        # add dna previews on top
        self.layout().addWidget(ui.panels.dna_views())
        # configuration panel on bottom
        self.layout().addWidget(ui.panels.configuration())


class main_window(QMainWindow):
    def __init__(self):
        # this is an inherented class of QMainWindow
        # so we must initialize the parent qt widget
        super().__init__()

        # configure the main window's general settings
        self.central_widget = central_widget()

        # utilize inhereted methods to set up the main window
        self.setWindowTitle("DNA Constructor")
        self.setCentralWidget(self.central_widget)

        # initilize status bar
        self._status_bar()

    def _status_bar(self):
        self.setStatusBar(QStatusBar())
        self.statusBar().setStyleSheet("background-color: rgb(220, 220, 220)")
