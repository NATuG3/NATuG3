from types import SimpleNamespace
from PyQt6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QDockWidget,
    QMenuBar,
    QMenu,
    QGroupBox,
    QHBoxLayout,
)
from PyQt6.QtCore import Qt
import ui
import webbrowser
import dna_nanotube_tools.graph

# START OF PLACEHOLDER CODE
domains = [dna_nanotube_tools.domain(9, 0)] * 14
side_view = dna_nanotube_tools.graph.side_view(domains, 3.38, 12.6, 2.3)
top_view = dna_nanotube_tools.graph.top_view(domains, 2.2)
# END OF PLACEHOLDER CODE


class main_window(QMainWindow):
    def __init__(self):
        # this is an inherented class of QMainWindow
        # so we must initialize the parent qt widget
        super().__init__()

        # utilize inhereted methods to set up the main window
        self.setWindowTitle("DNA Constructor")

        # the side view plot is the main widget
        self.setCentralWidget(ui.plots.side_view())

        # initilize status bar
        self._status_bar()

        # initilize menu bar
        self._menu_bar()

        # add docked widgets
        self._docked_widgets()

    def _docked_widgets(self):
        """Add all docked widgets."""
        # docked widget positions:
        #  0x1 left, 0x2 right; 0x4 top; 0x8 bottom; 0 all

        # attach top view to left dock
        self.top_view = QDockWidget()
        self.top_view.setWindowTitle("Top View of Helicies")
        self.top_view.setStatusTip("A plot of the top view of all domains")
        self.top_view.setWidget(ui.plots.top_view())
        self.top_view.setMaximumWidth(270)
        self.top_view.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )
        self.addDockWidget(Qt.DockWidgetArea(0x1), self.top_view)

        # attach config panel to right dock
        self.config = QDockWidget()
        self.config.setWindowTitle("Config")
        self.config.setStatusTip("Settings panel")
        self.config.setWidget(ui.panels.config())
        self.config.setMaximumWidth(250)
        self.config.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )
        self.addDockWidget(Qt.DockWidgetArea(0x2), self.docked_widgets.config)

    def _status_bar(self):
        """Create and add status bar."""
        self.setStatusBar(QStatusBar())
        self.statusBar().setStyleSheet("background-color: rgb(210, 210, 210)")

    def _menu_bar(self):
        """Create a menu bar for the main window"""
        self.menu_bar = QMenuBar()

        def hide_or_unhide(widget):
            """
            Reverse the hiddenness of a widget
            """
            if widget.isHidden():
                widget.show()
            else:
                widget.hide()

        class view(QMenu):
            def __init__(subself):
                super().__init__("&View", self.menu_bar)

                subself.actions = SimpleNamespace()

                # view -> "settings" -> hide/unhide
                subself.actions.config = subself.addAction("Config")
                subself.actions.config.setStatusTip("Display the config tab menu")
                subself.actions.config.setChecked(True)
                subself.actions.config.setCheckable(True)
                subself.actions.config.toggled.connect(
                    lambda: hide_or_unhide(self.docked_widgets.config)
                )

                # view -> "top view" -> hide/unhide
                subself.actions.top_view = subself.addAction("Helicies Top View")
                subself.actions.config.setStatusTip(
                    "Display the helicies top view graph"
                )
                subself.actions.top_view.setChecked(True)
                subself.actions.top_view.setCheckable(True)
                subself.actions.top_view.toggled.connect(
                    lambda: hide_or_unhide(self.docked_widgets.top_view)
                )

        class help(QMenu):
            def __init__(subself):
                super().__init__("&Help", self.menu_bar)

                # help -> manual -> open manual pdf
                subself.actions = SimpleNamespace()
                subself.actions.manual = subself.addAction("Manual")

                # help -> github -> open github project link
                subself.actions.github = subself.addAction("Github")
                subself.actions.github.triggered.connect(
                    lambda: webbrowser.open_new_tab(
                        "https://github.com/404Wolf/dna_nanotube_tools"
                    )
                )

                # help -> about -> open about statement
                subself.actions.about = subself.addAction("About")

        # add all the menus to the filemenu
        self.menu_bar.addMenu(view())
        self.menu_bar.addMenu(help())

        # place the menu bar object into the actual menu bar
        self.setMenuBar(self.menu_bar)
