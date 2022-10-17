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
    QWidget,
)

import config.domains.storage
import config.main
import config.nucleic_acid
import storage

logger = logging.getLogger(__name__)


class Window(QMainWindow):
    """
    The application's main window.

    Attributes:
        panels (SimpleNamespace): All docked widgets.
        status_bar (QStatusBar): The status bar.
        menu_bar (QMenuBar): The menu bar.
        top_view (QWidget): Top view widget.
        side_view (QWidget): Side view widget.
    """

    def __init__(self):
        # this is an inherited class of QMainWindow,
        # so we must initialize the parent qt widget
        super().__init__()

        # create plot panels
        self.panels = SimpleNamespace()  # container for all panels
        self._top_view()
        self._side_view()

        # utilize inherited methods to set up the main window
        self.setWindowTitle(config.name)

        # add all widgets
        self._config()

        # initialize status bar
        self._status_bar()

        # initialize menu bar
        self._menu_bar()

    def _config(self):
        # create a dockable config widget
        self.panels.config = QDockWidget()

        # set titles/descriptions
        self.panels.config.setObjectName("Config Panel")
        self.panels.config.setStatusTip("Config panel")
        self.panels.config.setWindowTitle("Config")

        # store the actual link to the widget in self.config
        self.config = config.main.Panel()
        self.panels.config.setWidget(self.config)

        self.panels.config.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        # trigger a resize event when the floatingness of the config panel changes
        self.panels.config.topLevelChanged.connect(self.resizeEvent)

        # trigger a resize event on tab change
        self.config.tab_area.currentChanged.connect(self.resizeEvent)

        # dock the new dockable config widget
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.panels.config)

    def _top_view(self):
        """Attach top view to main window/replace current top view widget"""
        # create dockable widget for top view
        self.panels.top_view = QDockWidget()

        # set titles/descriptions
        self.panels.top_view.setObjectName("Top View")
        self.panels.top_view.setWindowTitle("Top View of Helices")
        self.panels.top_view.setStatusTip("A plot of the top view of all domains")

        # attach actual top view widget to docked top view widget
        self.panels.top_view.setWidget(storage.plots.top_view.ui())

        # top view is only allowed on the sides
        self.panels.top_view.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        # trigger a resize event when the floatingness of the side view panel changes
        self.panels.top_view.topLevelChanged.connect(self.resizeEvent)

        # dock the new dockable top view widget
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.panels.top_view)

        logger.info("Loaded top view graph.")

    def _side_view(self):
        """Attach side view to main window/replace current side view widget"""
        # create group box to place side view widget in
        self.side_view = QGroupBox()
        self.side_view.setObjectName("Side View")
        self.side_view.setLayout(QVBoxLayout())
        self.side_view.setTitle("Side View of Helices")
        self.side_view.setStatusTip("A plot of the side view of all domains")

        # add actual plot to GroupBox
        self.side_view.layout().addWidget(storage.plots.side_view.ui())

        # set the central widget of the window
        self.setCentralWidget(self.side_view)

        logger.info("Loaded side view graph.")

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
        import windows.constructor.menus as menus

        # add all the menus to the filemenu
        self.menu_bar.addMenu(menus.File(self))
        self.menu_bar.addMenu(menus.View(self))
        self.menu_bar.addMenu(menus.Help(self))

        # place the menu bar object into the actual menu bar
        self.setMenuBar(self.menu_bar)
        logger.info("Created menu bar.")

    def resizeEvent(self, event):
        """
        Changes size of various widgets dynamically based on the main window's size.

        Notes:
            - If domain tab of config panel is showing, makes config panel pop out and larger
            - If domain tab of config panel is not showing, makes config panel unpop out and smaller
        """
        # side view resizing
        #
        self.centralWidget().setMinimumWidth(int(4 * self.size().width() / 9))

        # top view resizing
        #
        # if the top view plot is floating make the max size very large
        if self.panels.top_view.isFloating():
            self.panels.top_view.setMaximumWidth(99999)
        # otherwise it can be resized up to 2/8ths of the screen
        else:
            self.panels.top_view.setMaximumWidth(round(2 * self.size().width() / 8))

        # config resizing
        #
        # if config is floating make the max size very large
        if self.panels.config.isFloating():
            self.panels.config.setMaximumWidth(600)
        # otherwise check the current tab of the config panel
        else:
            # if the domains tab of the config panel is visible:
            if self.config.tabs.domains.isVisible():
                # set the maximum width of config to be 3/8ths of the screen, and the minimum possible size
                # to be that of the domain tab's width
                self.panels.config.setFixedWidth(265)
            # if the nucleic acid tab of the config panel is visible:
            elif self.config.tabs.nucleic_acid.isVisible():
                self.panels.config.setMaximumWidth(round(2 * self.size().width() / 8))
                self.panels.config.setMinimumWidth(0)
