from PyQt6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QDockWidget,
    QMenuBar,
    QVBoxLayout,
    QGroupBox,
)
import ui.widgets, ui.widgets.config, ui.slots
from PyQt6.QtCore import Qt
from contextlib import suppress
import database.ui


class window(QMainWindow):
    def __init__(self):
        # this is an inherented class of QMainWindow
        # so we must initialize the parent qt widget
        super().__init__()

        # store instance in the database
        database.ui.window = self

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

        # store widget in database for cross-module access
        database.ui.widgets.top_view = ui.widgets.top_view()
        self.top_view.setWidget(database.ui.widgets.top_view)

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
        # convert from QWidget to QGroupBox for pretty label and frame
        self.side_view = QGroupBox()
        self.side_view.setLayout(QVBoxLayout())
        self.side_view.setTitle("Side View of Helicies")
        self.side_view.setStatusTip("A plot of the side view of all domains")

        # store widget in database for cross-module access
        database.ui.widgets.side_view = ui.widgets.side_view()
        self.side_view.layout().addWidget(database.ui.widgets.side_view)

        # ensure this widget is always large enough to be useful (300px)
        self.side_view.setMinimumWidth(300)
        self.setCentralWidget(self.side_view)

    def _status_bar(self):
        """Create and add status bar."""
        self.setStatusBar(QStatusBar())
        self.statusBar().setStyleSheet("background-color: rgb(210, 210, 210)")

    def _menu_bar(self):
        """Create a menu bar for the main window"""
        # create menu bar
        self.menu_bar = QMenuBar()

        # import all menu bars
        import ui.menu_bars

        # add all the menus to the filemenu
        self.menu_bar.addMenu(ui.menu_bars.file())
        self.menu_bar.addMenu(ui.menu_bars.view())
        self.menu_bar.addMenu(ui.menu_bars.help())

        # place the menu bar object into the actual menu bar
        self.setMenuBar(self.menu_bar)
