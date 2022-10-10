import logging
from types import SimpleNamespace

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QDockWidget,
    QMenuBar,
    QVBoxLayout,
    QGroupBox,
    QWidget,
)

import config.main
import config.nucleic_acid
import config.domains.storage
import plotting.side_view.runner
import plotting.top_view.runner
import references

logger = logging.getLogger(__name__)


class Window(QMainWindow):
    """
    The application's main window.

    Attributes:
        docked_widgets (SimpleNamespace): All docked widgets.
        status_bar (QStatusBar): The status bar.
        menu_bar (QMenuBar): The menu bar.
        top_view (QWidget): Top view widget.
        side_view (QWidget): Side view widget.
    """

    def __init__(self):
        # this is an inherited class of QMainWindow,
        # so we must initialize the parent qt widget
        super().__init__()

        # store a reference to self in references for cross module use
        references.constructor = self

        # utilize inherited methods to set up the main window
        self.setWindowTitle("DNA Constructor")

        # initialize status bar
        self._status_bar()

        # initialize menu bar
        self._menu_bar()

        # container to store references to all docked widgets
        self.docked_widgets = SimpleNamespace()

        # add all widgets
        self.load_graphs()
        self._config()

    def load_graphs(self):
        """Load all nanotube graphs simultaneously."""
        self._top_view()
        self._side_view()

    def _config(self):
        # create a dockable config widget
        self.docked_widgets.config = QDockWidget()

        # set titles/descriptions
        self.docked_widgets.config.setObjectName("Config Panel")
        self.docked_widgets.config.setStatusTip("Config panel")
        self.docked_widgets.config.setWindowTitle("Config")

        # store the actual link to the widget in self.config
        self.config = config.main.Panel()
        self.docked_widgets.config.setWidget(self.config)

        # floating will be determined by current tab (see self.resizeEvent)
        self.docked_widgets.config.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
        )

        self.docked_widgets.config.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        # trigger a resize event when the floatingness of the config panel changes
        self.docked_widgets.config.topLevelChanged.connect(self.resizeEvent)

        # dock the new dockable config widget
        self.addDockWidget(
            Qt.DockWidgetArea.RightDockWidgetArea, self.docked_widgets.config
        )

    def _top_view(self):
        """Attach top view to main window/replace current top view widget"""
        try:
            assert isinstance(self.top_view, QWidget)
            self.top_view.load()
            logger.info("Reloaded top view graph.")
        except AttributeError:
            # create dockable widget for top view
            self.docked_widgets.top_view = QDockWidget()

            # set titles/descriptions
            self.docked_widgets.top_view.setObjectName("Top View")
            self.docked_widgets.top_view.setWindowTitle("Top View of Helices")
            self.docked_widgets.top_view.setStatusTip(
                "A plot of the top view of all domains"
            )

            # store widget in class for easier direct access
            self.top_view = plotting.top_view.runner.Plot()

            # attach actual top view widget to docked top view widget
            self.docked_widgets.top_view.setWidget(self.top_view)

            # top view is only allowed on the sides
            self.docked_widgets.top_view.setAllowedAreas(
                Qt.DockWidgetArea.LeftDockWidgetArea
                | Qt.DockWidgetArea.RightDockWidgetArea
            )

            # trigger a resize event when the floatingness of the side view panel changes
            self.docked_widgets.top_view.topLevelChanged.connect(self.resizeEvent)

            # dock the new dockable top view widget
            self.addDockWidget(
                Qt.DockWidgetArea.LeftDockWidgetArea, self.docked_widgets.top_view
            )

            logger.info("Loaded top view graph for the first time.")

    def _side_view(self):
        """Attach side view to main window/replace current side view widget"""
        try:
            assert isinstance(self.side_view, QWidget)
            self.side_view.load()
            logger.info("Reloaded side view graph.")
        except AttributeError:
            # create group box to place side view widget in
            prettified_side_view = QGroupBox()
            prettified_side_view.setObjectName("Side View")
            prettified_side_view.setLayout(QVBoxLayout())
            prettified_side_view.setTitle("Side View of Helices")
            prettified_side_view.setStatusTip("A plot of the side view of all domains")

            # create side view plot
            self.side_view = plotting.side_view.runner.Plot()

            # store widget in class for easier future direct widget access
            prettified_side_view.layout().addWidget(self.side_view)

            # set side view as the main widget
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
        import windows.constructor.menus as menus

        # add all the menus to the filemenu
        self.menu_bar.addMenu(menus.File())
        self.menu_bar.addMenu(menus.view())
        self.menu_bar.addMenu(menus.help())

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
        self.side_view.setMinimumWidth(int(4 * self.size().width() / 9))

        # top view resizing
        #
        # if the top view plot is floating make the max size very large
        if self.docked_widgets.top_view.isFloating():
            self.docked_widgets.top_view.setMaximumWidth(99999)
        # otherwise it can be resized up to 2/8ths of the screen
        else:
            self.docked_widgets.top_view.setMaximumWidth(
                round(2 * self.size().width() / 8)
            )

        # config resizing
        #
        # if config is floating make the max size very large
        if self.docked_widgets.config.isFloating():
            self.docked_widgets.config.setMaximumWidth(600)
        # otherwise check the current tab of the config panel
        else:
            # if the domains tab of the config panel is visible:
            if self.config.tabs.domains.isVisible():
                # set the maximum width of config to be 3/8ths of the screen, and the minimum possible size
                # to be that of the domain tab's width
                self.docked_widgets.config.setMaximumWidth(
                    round(3 * self.size().width() / 8)
                )
                self.docked_widgets.config.setMinimumWidth(265)
            # if the nucleic acid tab of the config panel is visible:
            elif self.config.tabs.nucleic_acid.isVisible():
                self.docked_widgets.config.setMaximumWidth(
                    round(2 * self.size().width() / 8)
                )
                self.docked_widgets.config.setMinimumWidth(0)
