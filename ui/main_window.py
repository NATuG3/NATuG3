from types import SimpleNamespace
from PyQt6.QtWidgets import QMainWindow, QStatusBar, QDockWidget, QMenuBar, QMenu
from PyQt6.QtCore import Qt
import ui
import webbrowser


class main_window(QMainWindow):
    def __init__(self):
        # this is an inherented class of QMainWindow
        # so we must initialize the parent qt widget
        super().__init__()

        # utilize inhereted methods to set up the main window
        self.setWindowTitle("DNA Constructor")
        self.setCentralWidget(ui.panels.central_panel())

        # attach config panel as docked panel
        self.config_panel = QDockWidget()
        self.config_panel.setWindowTitle("Configuration")
        self.config_panel.setWidget(ui.panels.configuration())
        self.config_panel.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable | QDockWidget.DockWidgetFeature.DockWidgetMovable)
        # 0x1 left, 0x2 right; 0x4 top; 0x8 bottom; 0 all
        self.addDockWidget(Qt.DockWidgetArea(0x2), self.config_panel)
        # initilize status bar
        self._status_bar()
        
        # initilize menu bar
        self._menu_bar()
        
    def _status_bar(self):
        self.setStatusBar(QStatusBar())
        self.statusBar().setStyleSheet("background-color: rgb(220, 220, 220)")

    def _menu_bar(self):
        self.menu_bar = QMenuBar()

        def hide_or_unhide(widget, action):
            if widget.isHidden():
                widget.show()
                action.setChecked(True)
            else:
                widget.hide()
                action.setChecked(False)

        class file(QMenu):
            def __init__(subself):
                super().__init__("&File", self.menu_bar)

                subself.actions = SimpleNamespace()
                subself.actions.open = subself.addAction("Open")
                subself.actions.save = subself.addAction("Save")

        class view(QMenu):
            def __init__(subself):
                super().__init__("&View", self.menu_bar)

                subself.actions = SimpleNamespace()
                
                subself.actions.side_view = subself.addAction("Helicies Side View")
                subself.actions.side_view.setChecked(True)
                subself.actions.side_view.setCheckable(True)
                subself.actions.side_view.triggered.connect(lambda: hide_or_unhide(self.centralWidget().widget(0), subself.actions.side_view))

                subself.actions.top_view = subself.addAction("Helicies Top View")
                subself.actions.top_view.setChecked(True)
                subself.actions.top_view.setCheckable(True)
                subself.actions.top_view.triggered.connect(lambda: hide_or_unhide(self.centralWidget().widget(1), subself.actions.top_view))

                subself.actions.top_view = subself.addAction("Settings")
                subself.actions.top_view.setChecked(True)
                subself.actions.top_view.setCheckable(True)
                subself.actions.top_view.triggered.connect(lambda: hide_or_unhide(self.config_panel, subself.actions.top_view))

        class help(QMenu):
            def __init__(subself):
                super().__init__("&Help", self.menu_bar)

                subself.actions = SimpleNamespace()
                subself.actions.manual = subself.addAction("Manual")

                subself.actions.github = subself.addAction("Github")
                subself.actions.github.triggered.connect(lambda: webbrowser.open_new_tab("https://github.com/404Wolf/dna_nanotube_tools"))

                subself.actions.about = subself.addAction("About")

        self.menu_bar.addMenu(file())
        self.menu_bar.addMenu(view())
        self.menu_bar.addMenu(help())

        self.setMenuBar(self.menu_bar)
        
        self.statusBar().setStyleSheet("background-color: rgb(220, 220, 220)")