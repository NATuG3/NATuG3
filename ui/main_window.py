from types import SimpleNamespace
from PyQt6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QMenuBar,
    QMenu,
    QGroupBox,
    QHBoxLayout,
)
import ui
import webbrowser
import dna_nanotube_tools.plot

# START OF PLACEHOLDER CODE
domains = [dna_nanotube_tools.domain(9, 0)] * 14
side_view = dna_nanotube_tools.plot.side_view(domains, 3.38, 12.6, 2.3)
top_view = dna_nanotube_tools.plot.top_view(domains, 2.2)
# END OF PLACEHOLDER CODE


class main_window(QMainWindow):
    def __init__(self):
        # this is an inherented class of QMainWindow
        # so we must initialize the parent qt widget
        super().__init__()

        # utilize inhereted methods to set up the main window
        self.setWindowTitle("DNA Constructor")

        # the side view plot is the main widget
        central_widget = QGroupBox()
        central_widget.setLayout(QHBoxLayout())
        central_widget.layout().addWidget(side_view.ui(150))
        central_widget.setTitle("Side View of Helicies")
        central_widget.setStatusTip("A plot of the side view of all domains")
        self.setCentralWidget(central_widget)

        # initilize status bar
        self._status_bar()

        # initilize menu bar
        self._menu_bar()

        # add docked widgets
        self._docked_widgets()

    def _docked_widgets(self):
        """Add all docked widgets."""

        # storage container for docked widget classes
        self.docked_widgets = SimpleNamespace()

        self.docked_widgets.top_view = ui.panels.top_view()
        self.addDockWidget(
            self.docked_widgets.top_view.area, self.docked_widgets.top_view
        )

        self.docked_widgets.config = ui.panels.config()
        self.addDockWidget(self.docked_widgets.config.area, self.docked_widgets.config)

    def _status_bar(self):
        """Create and add status bar."""
        self.setStatusBar(QStatusBar())
        self.statusBar().setStyleSheet(
            "background-color: rgb(210, 210, 210); margin-top: 10px"
        )

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
