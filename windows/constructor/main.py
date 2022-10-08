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
from PyQt6.QtGui import QScreen

import config.main
import config.nucleic_acid
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
    """

    def __init__(self):
        # this is an inherited class of QMainWindow,
        # so we must initialize the parent qt widget
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
        self.load_graphs()
        self._config()

        # scale widgets
        self.resizeEvent(None)

        # move main window to center of the screen
        # https://stackoverflow.com/a/63132944

        center_point = QScreen.availableGeometry(references.app.primaryScreen()).center()
        fg = self.frameGeometry()
        fg.moveCenter(center_point)
        self.move(fg.topLeft())

    def _config(self):
        # create a dockable config widget
        self.docked_widgets.config = QDockWidget()
        self.docked_widgets.config.setObjectName("Config Panel")
        self.docked_widgets.config.setWindowTitle("Config")
        self.docked_widgets.config.setStatusTip("Config panel")

        # store the actual link to the widget in self.config
        self.config = config.main.panel()
        self.docked_widgets.config.setWidget(self.config)

        # floating will be determined by current tab (see self.resizeEvent)
        self.docked_widgets.config.setFeatures(QDockWidget.DockWidgetFeature.NoDockWidgetFeatures)

        # remove config scaling limitations when config becomes floating
        self.docked_widgets.config.topLevelChanged.connect(self.resizeEvent)

        # dock the new dockable config widget
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.docked_widgets.config)

    def load_graphs(self):
        """Load all nanotube graphs simultaneously."""
        self._top_view()
        self._side_view()

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

            self.docked_widgets.top_view.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea)
            self.docked_widgets.top_view.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetFloatable)

            self.docked_widgets.top_view.topLevelChanged.connect(self.resizeEvent)

            # dock the new dockable top view widget
            self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.docked_widgets.top_view)

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
        self.menu_bar.addMenu(menus.file())
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
        # Resize various windows based on the size of the screen
        window_width = self.width()  # obtain width of the main window

        # side view resizing
        #
        self.side_view.setMinimumWidth(int(3 * window_width / 7))

        # top view resizing
        #
        # set extra large width of the config panel if it is floating
        if self.docked_widgets.top_view.isFloating():
            self.docked_widgets.top_view.setMinimumWidth(350)
            self.docked_widgets.top_view.setMaximumWidth(99999)
        # set reasonably sized width of not floating panel
        else:
            self.docked_widgets.top_view.setMinimumWidth(200)
            self.docked_widgets.top_view.setMaximumWidth(int(2 * window_width / 7))

        # config resizing
        #
        # if the config panel's domain tab is visible make the config panel float
        # and make it half the width of the main panel
        if self.config.tabs.domains.isVisible():
            self.docked_widgets.config.setFloating(True)
            self.docked_widgets.config.setMinimumWidth(int(window_width / 2))
        # if the config panel's domain tab is not visible then unfloat the config panel
        else:
            self.docked_widgets.config.setFloating(False)
            # resize the main window to prevent the unfloating from net-increasing the main window's width
            self.resize(self.width()-200, self.height())
            self.docked_widgets.config.setMinimumWidth(200)
            self.docked_widgets.config.setMaximumWidth(int(2 * window_width / 7))


