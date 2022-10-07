import logging
from types import SimpleNamespace

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QDockWidget,
    QMenuBar,
    QVBoxLayout,
    QGroupBox,
    QWidget
)

import config
import helpers
import plotting.side_view.runner
import plotting.top_view.runner
import references

logger = logging.getLogger(__name__)


class window(QMainWindow):
    """
    The application's main window.

    Attributes:
        docked_widgets (SimpleNamespace): All docked widgets.
        status_bar (QStatusBar): The status bar.
        menu_bar (QMenuBar): The menu bar.
        top_view (QWidget): Top view widget.
        side_view (QWidget): Side view widget.
        config (QDockWidget): Config panel.
    """

    def __init__(self):
        super().__init__()

        # store a reference to self in references for cross module use
        references.windows.constructor = self

        # utilize inherited methods to set up the main window
        self.setWindowTitle("DNA Constructor")

        # initialize status bar
        self._status_bar()

        # initialize menu bar
        self._menu_bar()

        # container to store references to all docked widgets
        self.docked_widgets = SimpleNamespace()

        # add all widgets
        self._top_view()
        self._side_view()
        self._config()

        # resize the widgets of the window based on the window's starting size
        self.resizeEvent(None)

    def _config(self):
        # create a dockable config widget
        self.docked_widgets.config = QDockWidget()
        self.docked_widgets.config.setObjectName("Config")
        self.docked_widgets.config.setWindowTitle("Config")
        self.docked_widgets.config.setStatusTip("Config")

        # store the actual link to the widget in self.config
        self.config = config.panel(self)
        self.docked_widgets.config.setWidget(self.config)

        self.docked_widgets.config.setAllowedAreas(
            # only left and right areas allowed
            Qt.DockWidgetArea(0x1)
            | Qt.DockWidgetArea(0x2)
        )

        # dock the new dockable config widget
        self.addDockWidget(Qt.DockWidgetArea(0x2), self.docked_widgets.config)

    def _top_view(self):
        """Attach top view to main window/replace current top view widget"""
        try:
            assert isinstance(self.top_view, QWidget)
            self.top_view.load()
            logger.info("Reloaded top view graph.")
        except AttributeError or AssertionError:
            # create dockable widget for top view
            self.docked_widgets.top_view = QDockWidget()
            self.docked_widgets.top_view.setObjectName("Top View")
            self.docked_widgets.top_view.setWindowTitle("Top View of Helices")
            self.docked_widgets.top_view.setStatusTip(
                "A plot of the top view of all domains"
            )

            # store widget in class for easier direct access
            self.top_view = plotting.top_view.runner.plot()

            # attach actual top view widget to docked top view widget
            self.docked_widgets.top_view.setWidget(self.top_view)

            # when this widget floats remove width scaling limitation
            self.docked_widgets.top_view.topLevelChanged.connect(
                lambda: helpers.unrestrict_scale_upon_float(
                    self.docked_widgets.top_view, initial_width=400
                )
            )

            self.docked_widgets.top_view.setAllowedAreas(
                # only left and right areas allowed
                Qt.DockWidgetArea(0x1)
                | Qt.DockWidgetArea(0x2)
            )

            # dock the new dockable top view widget
            self.addDockWidget(Qt.DockWidgetArea(0x1), self.docked_widgets.top_view)

            logger.info("Loaded top view graph for the first time.")

    def _side_view(self):
        """Attach side view to main window/replace current side view widget"""
        try:
            assert isinstance(self.side_view, QWidget)
            self.side_view.load()
            logger.info("Reloaded side view graph.")
        except AttributeError or AssertionError:
            # create group box to place side view widget in
            prettified_side_view = QGroupBox()
            prettified_side_view.setObjectName("Side View")
            prettified_side_view.setLayout(QVBoxLayout())
            prettified_side_view.setTitle("Side View of Helices")
            prettified_side_view.setStatusTip("A plot of the side view of all domains")

            # store widget in class for easier future direct widget access
            self.side_view = plotting.side_view.runner.plot()
            prettified_side_view.layout().addWidget(self.side_view)

            # make side view plot the main window's central widget
            self.setCentralWidget(prettified_side_view)

            logger.info("Loaded side view graph for the first time.")

    def _status_bar(self):
        """Create and add status bar."""
        status_bar = self.status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        self.statusBar().setStyleSheet("background-color: rgb(210, 210, 210)")
        logger.info("Created status bar.")

    def _menu_bar(self):
        """Create a menu bar for the main window"""
        # create menu bar
        self.menu_bar = QMenuBar()

        # import all menu bars
        import constructor.menus as menus

        # add all the menus to the file menu
        self.menu_bar.addMenu(menus.file())
        self.menu_bar.addMenu(menus.view())
        self.menu_bar.addMenu(menus.help())

        # place the menu bar object into the actual menu bar
        self.setMenuBar(self.menu_bar)
        logger.info("Created menu bar.")

    def resizeEvent(self, resizeEvent):
        """Triggers on window resize"""
        # Resize various windows based on the size of the screen
        window_width = self.width()  # obtain width of the main window

        # side view resizing
        #
        # minimum width = window_width/2.5
        # maximum width = no maximum width
        self.side_view.setMinimumWidth(int(window_width / 2.5))

        # top view resizing
        #
        # minimum width = half of the width of the config panel
        # maximum width = window_width/3.5 (if smaller than config panel's width then set to the config panel's width)
        if not self.docked_widgets.top_view.isFloating():
            new_width = int(window_width / 3.5)
            if new_width < self.config.width():
                new_width = self.config.width()
            self.docked_widgets.top_view.setMaximumWidth(new_width)
            self.docked_widgets.top_view.setMinimumWidth(int(self.config.width() / 2))

        # config resizing
        #
        # width = 200 if window_width / 5 < 200
        if window_width // 5 < 200:
            self.config.setFixedWidth(200)
        # width = 200 if window_width / 5 > 500
        elif window_width // 5 > 500:
            self.config.setFixedWidth(300)
        # normally the config panel's width = window width / 5
        else:
            self.config.setFixedWidth(int(window_width // 5))
