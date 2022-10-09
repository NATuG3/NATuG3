import logging
from types import SimpleNamespace
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import config.nucleic_acid, config.domains, config.main
import references
from resources import fetch_icon

count = 50
logger = logging.getLogger(__name__)


class Panel(QWidget):
    """Config panel."""

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("config/panel.ui", self)

        # call setup functions
        self._styling()
        self._tabs()

    def _styling(self):
        """Set icons/stylesheets/other styles for config panel."""
        self.update_graphs.setIcon(fetch_icon("reload-outline"))

    def _tabs(self):
        """Set up all tabs for config panel."""
        logger.debug("Building config panel...")

        def build():
            """Build all tabs"""
            # container to store tabs in
            self.tabs = SimpleNamespace()

            # set the nucleic acid tab
            # store actual widget in the tabs container
            self.tabs.nucleic_acid = config.nucleic_acid.Panel(self)
            self.nucleic_acid_tab.setLayout(QVBoxLayout())
            self.nucleic_acid_tab.layout().addWidget(self.tabs.nucleic_acid)

            # set the domains tab
            # store actual widget in the tabs container
            self.tabs.domains = config.domains.Panel()
            self.domains_tab.setLayout(QVBoxLayout())
            self.domains_tab.layout().addWidget(self.tabs.domains)

            # set up the update graphs button
            self.update_graphs.clicked.connect(references.constructor.load_graphs)

        build()

        def tab_changed():
            """Current tab changed event"""
            # obtain the dockable config panel from the main window reference
            config_panel = references.constructor.docked_widgets.config

            # if any of these tabs are visible then the config panel will float
            float_on_visible_tabs = [self.tabs.domains]

            if any([item.isVisible() for item in float_on_visible_tabs]):
                # make the config panel float
                config_panel.setFloating(True)

                # increase the width of the config panel
                config_panel.setFixedWidth(375)

                # set the height of the domains table to be
                # the height of a singular domain entry * number of domains
                desired_config_height = 45 * len(config.domains.storage.current)
                screen_size = references.app.primaryScreen().size().height()

                # but if this would require making the domains table taller than the actual screen size,
                # just set the domains table height to the screen size
                if desired_config_height > screen_size:
                    config_panel.setMinimumHeight(screen_size)
                else:
                    config_panel.setMinimumHeight(desired_config_height)
                    # now that the height has grown allow the height to shrink again
                    config_panel.setMinimumHeight(0)
            else:
                # undo any set minimum height on the config panel
                config_panel.setMinimumHeight(0)
                # no longer float the config panel
                config_panel.setFloating(False)
                # force a resize of the config panel now that it is re-docked
                references.constructor.resizeEvent(None)

        # if user attempts to unfloat domain tab don't let them
        references.constructor.docked_widgets.config.topLevelChanged.connect(
            tab_changed
        )
        # if user changes to certain tabs change size of the config panel/potentially float it
        self.tab_area.currentChanged.connect(tab_changed)
