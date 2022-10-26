import logging

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QMenuBar,
    QWidget,
)

import settings

logger = logging.getLogger(__name__)


class Window(QMainWindow):
    """
    The application's references window.

    Attributes:
        panels: All docked widgets.
        status_bar (QStatusBar): The status bar.
        menu_bar (QMenuBar): The menu bar.
        top_view (QWidget): Top view widget.
        side_view (QWidget): Side view widget.
    """

    class panels:
        __slots__ = ("config", "top_view", "side_view")

    def __init__(self):
        # this is an inherited class of QMainWindow,
        # so we must initialize the parent qt widget
        super().__init__()

        # create plot panels
        self._top_view()
        self._side_view()

        # utilize inherited methods to set up the references window
        self.setWindowTitle(settings.name)

        # add all widgets
        self._config()

        # initialize status bar
        self._status_bar()

        # initialize menu bar
        self._menu_bar()

    def _config(self):
        """Setup config panel."""

        # import the needed panel
        import constructor.panels.config

        # initialize the config panel
        self.config = constructor.panels.config.Panel()

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
        from constructor.panels import TopView

        self.top_view = TopView()

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
        from .panels import SideView

        self.side_view = SideView()

        # set the central widget of the window
        self.setCentralWidget(self.side_view)

        logger.info("Loaded side view graph.")

    def _status_bar(self):
        """Setup status bar."""
        status_bar = self.status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        self.statusBar().setStyleSheet("background-color: rgb(210, 210, 210)")
        logger.info("Created status bar.")

    def _menu_bar(self):
        """Setup menu bar."""
        self.menu_bar = QMenuBar()

        # import all menu bars
        from .menus import File, View, Help

        # add all the menus to the filemenu
        self.menu_bar.addMenu(File(self))
        self.menu_bar.addMenu(View(self))
        self.menu_bar.addMenu(Help(self))

        # place the menu bar object into the actual menu bar
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
            self.top_view.setMaximumWidth(round(2.5 * self.size().width() / 8))

        # config resizing...
        # if config is floating make the max size very large
        if self.config.isFloating():
            self.config.setMaximumWidth(600)
        # otherwise check the current tab of the config panel
        else:
            # if the domains tab of the config panel is visible:
            if self.config.panel.tabs.domains.isVisible():
                # set the maximum width of config to be 3/8ths of the screen, and the minimum possible size
                # to be that of the domain tab's width
                self.config.setFixedWidth(270)
            # if the nucleic acid tab of the config panel is visible:
            elif self.config.panel.tabs.nucleic_acid.isVisible():
                self.config.setFixedWidth(200)
