import logging
from types import SimpleNamespace

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QTableWidget, QHeaderView, QAbstractItemView

import configuration.domains.storage
from configuration.domains.widgets import *
from constants.directions import *
from resources.workers import fetch_icon

logger = logging.getLogger(__name__)


class Panel(QWidget):
    """Nucleic Acid Config Tab."""

    def __init__(self) -> None:
        super().__init__()

        # load in the panel's designer UI
        uic.loadUi("configuration/domains/panel.ui", self)

        # set reload table widget
        self.update_table.setIcon(fetch_icon("reload-outline"))

        # create domains editor table and append it to the bottom of the domains panel
        self.table = Table(self)
        self.layout().addWidget(self.table)

        # set initial values of domain table configuration widgets
        self.subunit_count.setValue(configuration.domains.storage.current.subunit.count)
        self.symmetry.setValue(configuration.domains.storage.current.symmetry)
        self.total_count.setValue(configuration.domains.storage.current.count)

        # hook update domains button
        self.update_table.clicked.connect(self.refresh)

        logger.info("Loaded domains tab of configuration panel.")
        self.table.helix_joint_updated.connect(self.updater)

    def updater(self):
        configuration.domains.storage.current.subunit.domains = self.table.load_domains()
        self.table.dump_domains(configuration.domains.storage.current.subunit.domains)

    def refresh(self):
        """Refresh panel settings/domain table."""
        # update storage settings
        configuration.domains.storage.current.subunit.count = self.subunit_count.value()
        configuration.domains.storage.current.symmetry = self.symmetry.value()

        # update settings boxes
        self.total_count.setValue(configuration.domains.storage.current.count)


class Table(QTableWidget):
    """Nucleic Acid Config Tab."""

    helix_joint_updated = pyqtSignal()

    def __init__(self, parent) -> None:
        super().__init__()
        # header storage areas
        self.side_headers = []
        self.top_headers = []

        # all current row data
        # (domain index = row index)
        self.rows = []

        # store parent object
        self.parent = parent

        # set up headers
        self._headers()

        # style the widget
        self._style()

        # dump the domains of the previous save
        self.dump_domains(configuration.domains.storage.current.subunit.domains)

    def _headers(self):
        """Configure top headers of widget"""
        # store headers (these do not change)
        self.top_headers = ("left", "right", "s", "m", "count")
        # create a column for each header
        self.setColumnCount(len(self.top_headers))
        # apply the headers
        self.setHorizontalHeaderLabels(self.top_headers)

    def _style(self):
        """Style the domain panel."""
        # set the style sheet of the panel
        self.setStyleSheet("QTableView::item{padding: 3.25px; text-align: center}")

        # show table grid
        self.setShowGrid(True)

        # enable smooth scrolling
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)

        # first two columns are statically sized
        for i in range(2):
            self.setColumnWidth(i, 35)
            self.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeMode.Fixed
            )

        # all others columns are dynamically sized
        for i in range(2, 6):
            self.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeMode.Stretch
            )

    def dump_domains(self, domains: list) -> None:
        """
        Dump a list of domain objects.

        Args:
            domains (List(Domain)): A list of all domains to dump
        """

        # create rows before we input widgets
        self.setRowCount(len(domains))

        # clear out the side headers list
        self.side_headers = []

        # container for current row items
        self.rows.clear()

        # insert all domains
        for index, domain in enumerate(domains):
            # container for currently-being-added widgets
            row = SimpleNamespace()

            # column 0 - left helical joint
            row.left_helix_joint = DirectionalButton(self, domain.helix_joints[LEFT])
            row.left_helix_joint.clicked.connect(self.helix_joint_updated.emit)
            self.setCellWidget(index, 0, row.left_helix_joint)

            # column 1 - right helical joint
            row.right_helix_joint = DirectionalButton(self, domain.helix_joints[RIGHT])
            row.right_helix_joint.clicked.connect(self.helix_joint_updated.emit)
            self.setCellWidget(index, 1, row.right_helix_joint)

            # column 2 - theta switch multiple
            row.theta_switch_multiple = TableIntegerBox(domain.theta_switch_multiple)
            row.theta_switch_multiple.setEnabled(False)
            self.setCellWidget(index, 2, row.theta_switch_multiple)

            # column 3 - theta interior multiple
            row.theta_interior_multiple = TableIntegerBox(domain.theta_interior_multiple, show_buttons=True, minimum=1, maximum=20)
            self.setCellWidget(index, 3, row.theta_interior_multiple)

            # column 4 - initial NEMid count
            row.domain_count = TableIntegerBox(domain.count)
            self.setCellWidget(index, 4, row.domain_count)

            self.side_headers.append(f"#{index + 1}")

            # append to the main row storage container
            self.rows.append(row)

        self.setVerticalHeaderLabels(self.side_headers)

    def load_domains(self) -> list:
        """
        Obtain a list of the currently chosen domains.

        Returns:
            List(domains): A list of domain objects based on user input.
        """
        domains = []  # output list of domains
        for domain in range(self.rowCount()):
            # column 0 - left helical joint
            left_helical_joint: Literal[UP, DOWN] = self.cellWidget(domain, 0).state

            # column 1 - right helical joint
            right_helical_joint: Literal[UP, DOWN] = self.cellWidget(domain, 1).state

            # column 2 - theta switch multiple
            # not needed since it can be calculated from left and right helical joints

            # column 3 - theta interior multiple
            theta_interior_multiple: int = self.cellWidget(domain, 3).value()

            # column 4 - initial NEMid count
            count: int = self.cellWidget(domain, 4).value()

            domain = configuration.domains.storage.Domain(
                theta_interior_multiple,
                (left_helical_joint, right_helical_joint),
                count,
            )

            domains.append(domain)

        return domains
