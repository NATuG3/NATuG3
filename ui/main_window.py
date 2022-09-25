from types import SimpleNamespace
from PyQt6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QMenuBar,
    QGroupBox,
    QVBoxLayout,
    QLabel,
)
import ui.menus
import dna_nanotube_tools.plot
import database.settings

# START OF PLACEHOLDER CODE
domains = [dna_nanotube_tools.domain(9, 0)] * 14
# END OF PLACEHOLDER CODE


class central_widget(QGroupBox):
    """Central widget of window"""

    def __init__(self):
        super().__init__("Side View of Helicies")

        # set main widget and layout
        self.setLayout(QVBoxLayout())

        # we store the previous widget so that it is easy to replace
        self.previous_widget = None

        # add plotted side view as main widget and apply styling
        self.setStatusTip("A plot of the side view of all domains")
        self.setMinimumWidth(350)

        # Refresh the side view central widget
        settings = database.settings.current_preset.data
        widget = dna_nanotube_tools.plot.side_view(
            domains,
            settings.Z_b,
            settings.Z_s,
            settings.theta_s,
            settings.theta_b,
            settings.theta_c,
        )
        widget = widget.ui(settings.count)
        self.layout().addWidget(widget)


class main_window(QMainWindow):
    def __init__(self):
        # this is an inherented class of QMainWindow
        # so we must initialize the parent qt widget
        super().__init__()

        # utilize inhereted methods to set up the main window
        self.setWindowTitle("DNA Constructor")

        # apply central widget
        self.setCentralWidget(central_widget())

        # initilize status bar
        self._status_bar()

        # initilize menu bar
        self._menu_bar()

        # add docked widgets
        self._docked_items()

        # initilize buttons
        self._buttons()

    def _buttons(self):
        """Link critical buttons"""
        # first overwrite the current preset
        def overwrite_current_preset():
            # obtain currently entered settings
            current_settings = (
                self.docked_items.config.tabs.settings.fetch_settings_data()
            )
            # overwrite the current preset
            database.settings.presets[
                database.settings.current_preset.name
            ] = current_settings
            database.settings.current_preset = SimpleNamespace(
                name=database.settings.current_preset.name, data=current_settings
            )
        self.docked_items.config.update_graphs_button.clicked.connect(
            overwrite_current_preset
        )

        # update graph button to graph refresh funcs
        self.docked_items.config.update_graphs_button.clicked.connect(
            lambda: self.docked_items.top_view.refresh()
        )
        self.docked_items.config.update_graphs_button.clicked.connect(
            lambda: self.setCentralWidget(central_widget())
        )

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
