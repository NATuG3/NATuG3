import logging
from types import SimpleNamespace

from PyQt6 import uic
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget,
    QTableWidget,
    QHeaderView,
    QAbstractItemView,
    QSizePolicy,
)

import references
import helpers

import settings
from constants.directions import *
from constructor.panels import domains
from constructor.panels.domains.widgets import *
from datatypes.domains import Domain
from resources.workers import fetch_icon
from constructor.panels.domains.table import Table

logger = logging.getLogger(__name__)


class Panel(QWidget):
    """Nucleic Acid Config Tab."""

    updated = pyqtSignal()

    def __init__(self, parent) -> None:
        super().__init__(parent)

        uic.loadUi("constructor/panels/domains/panel.ui", self)

        # set reload table widget
        self.update_table.setIcon(fetch_icon("checkmark-outline"))

        # create domains editor table and append it to the bottom of the domains panel
        self.table = Table(self)
        self.layout().addWidget(self.table)

        # set scaling settings for config and references table
        config_size_policy = QSizePolicy()
        config_size_policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)
        config_size_policy.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        self.config.setSizePolicy(config_size_policy)

        # set initial values of domain table config widgets
        self.subunit_count.setValue(references.domains.current.subunit.count)
        self.symmetry.setValue(references.domains.current.symmetry)
        self.total_count.setValue(references.domains.current.count)

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
        references.domains.current.subunit.domains = self.table.fetch_domains()

        confirmation: bool = True
        # double-check with user if they want to truncate the domains/subunit count
        # (if that is what they are attempting to do)
        if self.subunit_count.value() < references.domains.current.subunit.count:
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
            references.domains.current.subunit.count = self.subunit_count.value()
            references.domains.current.symmetry = self.symmetry.value()

            # update settings boxes
            self.total_count.setValue(references.domains.current.count)

            self.update_table.setStyleSheet(
                f"background-color: rgb{str(settings.colors.green)}"
            )
            timer = QTimer(self.parent())
            timer.setInterval(400)
            timer.setSingleShot(True)
            timer.timeout.connect(
                lambda: self.update_table.setStyleSheet("background-color: light grey")
            )
            timer.start()

        # refresh table
        self.table.dump_domains(references.domains.current.subunit.domains)
