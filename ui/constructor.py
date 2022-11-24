import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QMenuBar,
    QWidget,
    QTabWidget,
)

import refs
import settings

logger = logging.getLogger(__name__)


class Window(QMainWindow):
    """
    The nanotube constructor main window.

    Attributes:
        status_bar (QStatusBar): The status bar.
        menu_bar (QMenuBar): The menu bar.
        toolbar (QToolBar): The toolbar.
        top_view (QWidget): Top view widget.
        side_view (QWidget): Side view widget.
    """

    def __init__(self):
        # this is an inherited class of QMainWindow,
        # so we must initialize the parent qt widget
        super().__init__()

        # store reference to self in refs
        refs.constructor = self

        # create plot panels
        self._top_view()
        self._side_view()

        # utilize inherited methods to set up the refs window
        self.setWindowTitle(settings.name)

        # add all widgets
        self._config()

        # initialize status bar
        self._status_bar()

        # initialize menu bar
        self._menu_bar()

        # initialize toolbar
        self._toolbar()

    def _toolbar(self):
        """Setup toolbar."""

        # import the needed panel
        from ui.toolbar import Toolbar

        self.toolbar = Toolbar(self)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

    def _config(self):
        """Setup config panel."""

        # import the needed panel
        from ui.panels.config import Dockable

        # initialize the config panel
        self.config = Dockable(self, refs.nucleic_acid.profiles, refs.domains.current)

        # only allow config to dock left/right
        self.config.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        # trigger a resize event when the floatingness of the config panel changes
        self.config.topLevelChanged.connect(self.resizeEvent)

        # trigger a resize event on tab change
        self.config.panel.tab_area.currentChanged.connect(self.resizeEvent)

        # dock the new dockable config widget
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.config)

    def _top_view(self):
        """Setup top view plot."""
        from ui.panels.top_view import Dockable

        self.top_view = Dockable(self)

        # set minimum width for top view
        self.top_view.setMinimumWidth(150)

        # top view is only allowed on the sides
        self.top_view.setAllowedAreas(
            Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea
        )

        # trigger a resize event when the floatingness of the side view panel changes
        self.top_view.topLevelChanged.connect(self.resizeEvent)

        # dock the new dockable top view widget
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.top_view)

        logger.info("Loaded top view graph.")

    def _side_view(self):
        """Setup side view plot."""
        from .panels.side_view import Panel

        self.side_view = Panel(self)

        # set the central widget of the window
        self.setCentralWidget(self.side_view)

        logger.info("Loaded side view graph.")

    def _status_bar(self):
        """Setup status bar."""
        status_bar = self.status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)
        self.statusBar().setStyleSheet("background-color: rgb(210, 210, 210)")
        logger.info("Created status bar.")

    def _menu_bar(self):
        """Setup menu bar."""
        from .menubar import Menubar

        self.menu_bar = Menubar()
        self.setMenuBar(self.menu_bar)

        logger.info("Created menu bar.")

    def resizeEvent(self, event):
        """Dynamically resize panels."""

        # side view resizing...
        self.centralWidget().setMinimumWidth(int(4 * self.size().width() / 9))

        # top view resizing...
        # if the top view plot is floating make the max size very large
        if self.top_view.isFloating():
            self.top_view.setMaximumWidth(99999)
        # otherwise it can be resized up to 2/8ths of the screen
        else:
            self.top_view.setMaximumWidth(round(2 * self.size().width() / 8))

        self.config.tab_area: QTabWidget
        # config resizing...
        # if config is floating make the max size very large
        if self.config.isFloating():
            self.config.tab_area.setTabPosition(QTabWidget.TabPosition.North)
            self.config.setMaximumWidth(600)
        # otherwise check the current tab of the config panel
        else:
            self.config.tab_area.setTabPosition(QTabWidget.TabPosition.East)
            # if the domains tab of the config panel is visible:
            if (
                self.config.panel.tabs.domains.isVisible()
                or self.config.panel.tabs.strands.isVisible()
            ):
                # set the maximum width of config to be 3/8ths of the screen, and the minimum possible size
                # to be that of the domain tab's width
                self.config.setFixedWidth(295)
            # if the nucleic acid tab of the config panel is visible:
            elif self.config.panel.tabs.nucleic_acid.isVisible():
                self.config.setFixedWidth(220)
