import logging

from PyQt6 import uic
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QSizePolicy,
)

import helpers
import refs
import settings
from ui.panels.domains.table import Table
from ui.resources import fetch_icon

logger = logging.getLogger(__name__)


class Panel(QWidget):
    """Nucleic Acid Config Tab."""

    updated = pyqtSignal()

    def __init__(self, parent) -> None:
        super().__init__(parent)

        uic.loadUi("ui/panels/domains/panel.ui", self)

        # set reload table widget
        self.update_table.setIcon(fetch_icon("checkmark-outline"))

        # create domains editor table and append it to the bottom of the domains panel
        self.table = Table(self)
        self.layout().addWidget(self.table)

        # set scaling settings for config and refs table
        config_size_policy = QSizePolicy()
        config_size_policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)
        config_size_policy.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        self.config.setSizePolicy(config_size_policy)

        # set initial values of domain table config widgets
        self.subunit_count.setValue(refs.domains.current.subunit.count)
        self.symmetry.setValue(refs.domains.current.symmetry)
        self.total_count.setValue(refs.domains.current.count)

        # hook update domains button
        self.update_table.clicked.connect(self.refresh)

        # updated event linking
        self.table.cell_widget_updated.connect(self.updated.emit)
        self.update_table.clicked.connect(self.updated.emit)

        logger.info("Loaded domains tab of config panel.")

        # update the "total domains" count box
        # when symmetry or subunit count are changed
        domain_counter = lambda: self.total_count.setValue(
            self.symmetry.value() * self.subunit_count.value()
        )
        self.symmetry.valueChanged.connect(domain_counter)
        self.subunit_count.valueChanged.connect(domain_counter)

        # when helix joint buttons are clicked refresh the table
        # so that the switch values (-1, 0, 1) get udpated
        self.table.helix_joint_updated.connect(
            lambda: self.table.dump_domains(self.table.fetch_domains())
        )

    def refresh(self):
        """Refresh panel settings/domain table."""
        # obtain current domain inputs
        refs.domains.current.subunit.domains = self.table.fetch_domains()

        confirmation: bool = True
        # double-check with user if they want to truncate the domains/subunit count
        # (if that is what they are attempting to do)
        if self.subunit_count.value() < refs.domains.current.subunit.count:
            # helpers.confirm will return a bool
            confirmation: bool = helpers.confirm(
                self.parent(),
                "Subunit Count Reduction",
                f"The prospective subunit count ({self.subunit_count.value()}) is lower than the number of domains in "
                f"the domains table ({self.table.rowCount()}). \n\nAre you sure you want to truncate the "
                f"domains/subunit count to {self.subunit_count.value()}?",
            )
        if confirmation:
            # update storage settings
            refs.domains.current.subunit.count = self.subunit_count.value()
            refs.domains.current.symmetry = self.symmetry.value()

            # update settings boxes
            self.total_count.setValue(refs.domains.current.count)

            self.update_table.setStyleSheet(
                f"background-color: rgb{str(settings.colors['success'])}"
            )
            timer = QTimer(self.parent())
            timer.setInterval(400)
            timer.setSingleShot(True)
            timer.timeout.connect(
                lambda: self.update_table.setStyleSheet("background-color: light grey")
            )
            timer.start()

        # refresh table
        self.table.dump_domains(refs.domains.current.subunit.domains)
