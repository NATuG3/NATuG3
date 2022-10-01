import logging
from types import SimpleNamespace
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import config.nucleic_acid, config.domains, config.main
import references
from resources import fetch_icon


count = 50
logger = logging.getLogger(__name__)


class panel(QWidget):
    """Config panel."""

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("config/designer/panel.ui", self)

        self.update_graphs.setIcon(fetch_icon("reload-outline"))

        # set config.panel.count (for cross module use)
        def config_count_updater():
            """Update config.panel.count to the current initial NEMid count box's value"""
            global count
            count = self.initial_NEMids.value()

        # store default value in initial_NEMids box
        self.initial_NEMids.setValue(config.main.count)
        # when initial NEMid count box is changed store the change
        self.initial_NEMids.valueChanged.connect(config_count_updater)

        # container to store tabs in
        self.tabs = SimpleNamespace()

        logger.debug("Building config panel...")
        # set the nucleic acid tab
        # store actual widget in the tabs container
        self.tabs.nucleic_acid = config.nucleic_acid.panel()
        self.nucleic_acid_tab.setLayout(QVBoxLayout())
        self.nucleic_acid_tab.layout().addWidget(self.tabs.nucleic_acid)

        # set the domains tab
        # store actual widget in the tabs container
        self.tabs.domains = config.domains.widget()
        self.domains_tab.setLayout(QVBoxLayout())
        self.domains_tab.layout().addWidget(self.tabs.domains)

        # set up the update graphs button
        self.update_graphs.clicked.connect(references.windows.constructor.load_graphs)
