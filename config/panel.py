from types import SimpleNamespace
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QVBoxLayout
import config.nucleic_acid, config.domains
import references


# general settings
count: int = None  # number of initial NEMids to generate


class panel(QWidget):
    """Config panel."""

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("config/ui/panel.ui", self)

        # set config.panel.count (for cross module use)
        def config_count_updater():
            """Update config.panel.count to the current initial NEMid count box's value"""
            config.panel.count = self.initial_NEMids.value()

        # store default value in initial_NEMids box
        config_count_updater()
        # when initial NEMid count box is changed store the change
        self.update_graphs.clicked.connect(config_count_updater)

        # container to store tabs in
        self.tabs = SimpleNamespace()

        # set the nucleic acid tab
        # store actual widget in the tabs container
        self.tabs.nucleic_acid = config.nucleic_acid.widget()
        self.nucleic_acid_tab.setLayout(QVBoxLayout())
        self.nucleic_acid_tab.layout().addWidget(self.tabs.nucleic_acid)

        # set the domains tab
        # store actual widget in the tabs container
        self.tabs.domains = config.domains.widget()
        self.domains_tab.setLayout(QVBoxLayout())
        self.domains_tab.layout().addWidget(self.tabs.domains)

        # set up the update graphs button
        self.update_graphs.clicked.connect(
            references.windows.constructor.load_graphs
        )
