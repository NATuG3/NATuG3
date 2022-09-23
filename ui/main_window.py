from PyQt6.QtWidgets import (
    QWidget,
    QMainWindow,
    QVBoxLayout,
    QLabel,
)
import ui


class central_widget(QWidget):
    def __init__(self) -> None:
        # this is an inherented class of QWidget
        # so we must initialize the parent qt widget
        super().__init__()

        # this is the main window's central widget, which is a vertical array layout
        self.layout = QVBoxLayout()
        # add dna previews on top
        self.layout.addWidget(ui.panels.dna_views())
        # configuration panel on bottom
        self.layout.addWidget(QLabel("Placeholder for configuration panel"))

        self.setLayout(self.layout)


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
