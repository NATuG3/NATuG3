from types import SimpleNamespace
from PyQt6.QtWidgets import QMainWindow, QStatusBar, QDockWidget, QMenuBar, QMenu
import ui.widgets, ui.widgets.config, ui.slots
import webbrowser
from PyQt6.QtCore import Qt
from contextlib import suppress
import database


class main_window(QMainWindow):
    def __init__(self):
        # this is an inherented class of QMainWindow
        # so we must initialize the parent qt widget
        super().__init__()

        # utilize inhereted methods to set up the main window
        self.setWindowTitle("DNA Constructor")

        # initilize status bar
        self._status_bar()

        # initilize menu bar
        self._menu_bar()

        # add all widgets
        self._config()
        self.refresh_top_view()
        self.refresh_side_view()

        # store instance in the database
        database.main_window = self

    def _config(self):
        # create a dockable config widget
        self.config = QDockWidget()
        self.config.setWindowTitle("Config")
        self.config.setStatusTip("Settings panel")
        self.config.setWidget(ui.widgets.config())
        # set width of config widget while docked to 200px
        self.config.setMinimumWidth(215)
        self.config.setMaximumWidth(215)
        # when this widget floats allow it to scale up to 400px wide
        self.config.topLevelChanged.connect(
            lambda: ui.slots.unrestrict_scale_upon_float(
                self.config, initial_width=215, unbounded_width=460
            )
        )
        self.config.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )
        # dock the new docakble config widget
        self.addDockWidget(Qt.DockWidgetArea(0x2), self.config)

    def refresh_top_view(self):
        """Attach top view to main window/replace current top view widget"""
        # remove the current top view widget if it exists
        with suppress(AttributeError):
            self.removeDockWidget(self.top_view)
        # create dockable widget for top view
        self.top_view = QDockWidget()
        self.top_view.setWindowTitle("Top View of Helicies")
        self.top_view.setStatusTip("A plot of the top view of all domains")
        self.top_view.setWidget(ui.widgets.top_view())
        # limit max width of top view widget while docked to 340px
        self.top_view.setMaximumWidth(340)
        # when this widget floats remove width scaling limitation
        self.top_view.topLevelChanged.connect(
            lambda: ui.slots.unrestrict_scale_upon_float(
                self.top_view, initial_width=340
            )
        )
        self.top_view.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )
        # dock the new dockable top view widget
        self.addDockWidget(Qt.DockWidgetArea(0x1), self.top_view)

    def refresh_side_view(self):
        """Attach side view to main window/replace current side view widget"""
        self.side_view = ui.widgets.side_view()
        # ensure this widget is always large enough to be useful (300px)
        self.side_view.setMinimumWidth(300)
        self.setCentralWidget(self.side_view)

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
