from PyQt6.QtWidgets import QWidget, QMainWindow, QVBoxLayout, QStatusBar, QDockWidget
from PyQt6.QtCore import Qt
import ui

class main_window(QMainWindow):
    def __init__(self):
        # this is an inherented class of QMainWindow
        # so we must initialize the parent qt widget
        super().__init__()

        # utilize inhereted methods to set up the main window
        self.setWindowTitle("DNA Constructor")
        self.setCentralWidget(ui.panels.central_panel())

        # attach config panel as docked panel
        config_panel = QDockWidget()
        config_panel.setWindowTitle("Configuration")
        config_panel.setWidget(ui.panels.configuration())
        config_panel.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
        # 0x1 left, 0x2 right; 0x4 top; 0x8 bottom; 0 all
        self.addDockWidget(Qt.DockWidgetArea(0x2), config_panel)

        # initilize status bar
        self._status_bar()

    def _status_bar(self):
        self.setStatusBar(QStatusBar())
        self.statusBar().setStyleSheet("background-color: rgb(220, 220, 220)")
