from types import SimpleNamespace
from PyQt6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QMenuBar,
    QGroupBox,
    QVBoxLayout,
)
import ui.menus
import dna_nanotube_tools.plot

# START OF PLACEHOLDER CODE
domains = [dna_nanotube_tools.domain(9, 0)] * 14
side_view = dna_nanotube_tools.plot.side_view(
    domains, 3.38, 12.6, 2.3, (360 / 21) * 2, 360 / 21
)
side_view = side_view.ui(150)
# END OF PLACEHOLDER CODE


class main_window(QMainWindow):
    def __init__(self):
        # this is an inherented class of QMainWindow
        # so we must initialize the parent qt widget
        super().__init__()

        # utilize inhereted methods to set up the main window
        self.setWindowTitle("DNA Constructor")

        # prittify the central widget in a group box
        class central_widget(QGroupBox):
            """Central widget of window"""

            def __init__(subself):
                super().__init__("Side View of Helicies")
                subself.setLayout(QVBoxLayout())
                subself.layout().addWidget(side_view)
                subself.setStatusTip("A plot of the side view of all domains")
                subself.setMinimumWidth(350)

        self.setCentralWidget(central_widget())

        # initilize status bar
        self._status_bar()

        # initilize menu bar
        self._menu_bar()

        # add docked widgets
        self._docked_items()

    def _docked_items(self):
        """Add all docked widgets."""

        # storage container for docked widget classes
        self.docked_items = SimpleNamespace()

        # dock the top view panel
        self.docked_items.top_view = ui.dockables.top_view()
        self.addDockWidget(self.docked_items.top_view.area, self.docked_items.top_view)

        # dock the side view panel
        self.docked_items.config = ui.dockables.config()
        self.addDockWidget(self.docked_items.config.area, self.docked_items.config)

    def _status_bar(self):
        """Create and add status bar."""
        self.setStatusBar(QStatusBar())
        self.statusBar().setStyleSheet(
            "background-color: rgb(210, 210, 210); margin-top: 10px"
        )

    def _menu_bar(self):
        """Create a menu bar for the main window"""

        # container to store menu bar items in
        self.menu_bar_items = SimpleNamespace()

        # initilize the menu bar
        self.setMenuBar(QMenuBar())

        # add all menus to the menu bar (and to the menu bar namespace container)
        self.menu_bar_items.view = ui.menus.view(self)
        self.menuBar().addMenu(self.menu_bar_items.view)

        self.menu_bar_items.help = ui.menus.help()
        self.menuBar().addMenu(self.menu_bar_items.help)
