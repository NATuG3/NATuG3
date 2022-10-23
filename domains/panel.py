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

import config
import domains.storage
import helpers
from constants.directions import *
from domains.widgets import *
from resources.workers import fetch_icon

logger = logging.getLogger(__name__)


class Panel(QWidget):
    """Nucleic Acid Config Tab."""

    def __init__(self, parent) -> None:
        super().__init__(parent)

        # load in the panel's designer UI
        uic.loadUi("domains/panel.ui", self)

        # set reload table widget
        self.update_table.setIcon(fetch_icon("checkmark-outline"))

        # create domains editor table and append it to the bottom of the domains panel
        self.table = Table(self)
        self.layout().addWidget(self.table)

        # set scaling settings for config and main table
        config_size_policy = QSizePolicy()
        config_size_policy.setVerticalPolicy(QSizePolicy.Policy.Fixed)
        config_size_policy.setHorizontalPolicy(QSizePolicy.Policy.Expanding)
        self.config.setSizePolicy(config_size_policy)

        # set initial values of domain table config widgets
        self.subunit_count.setValue(domains.storage.current.subunit.count)
        self.symmetry.setValue(domains.storage.current.symmetry)
        self.total_count.setValue(domains.storage.current.count)

        # hook update domains button
        self.update_table.clicked.connect(self.refresh)

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
        domains.storage.current.subunit.domains = self.table.fetch_domains()

        confirmation: bool = True
        # double-check with user if they want to truncate the domains/subunit count
        # (if that is what they are attempting to do)
        if self.subunit_count.value() < domains.storage.current.subunit.count:
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
            domains.storage.current.subunit.count = self.subunit_count.value()
            domains.storage.current.symmetry = self.symmetry.value()

            # update settings boxes
            self.total_count.setValue(domains.storage.current.count)

            self.update_table.setStyleSheet(
                f"background-color: rgb{str(config.colors.green)}"
            )
            timer = QTimer(self.parent())
            timer.setInterval(400)
            timer.setSingleShot(True)
            timer.timeout.connect(
                lambda: self.update_table.setStyleSheet("background-color: light grey")
            )
            timer.start()

        # refresh table
        self.table.dump_domains(domains.storage.current.subunit.domains)


class Table(QTableWidget):
    """Nucleic Acid Config Tab."""

    helix_joint_updated = pyqtSignal()
    cell_widget_updated = pyqtSignal()

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
        self.dump_domains(domains.storage.current.subunit.domains)

        # when widget value is changed run fetch_domains and update current settings
        @self.cell_widget_updated.connect
        def _():
            domains.storage.current.subunit.domains = self.fetch_domains()

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
            domains (List(Domain)): A list of all domains to dump.
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
            row.left_helix_joint.clicked.connect(self.cell_widget_updated.emit)
            self.setCellWidget(index, 0, row.left_helix_joint)

            # column 1 - right helical joint
            row.right_helix_joint = DirectionalButton(self, domain.helix_joints[RIGHT])
            row.right_helix_joint.clicked.connect(self.helix_joint_updated.emit)
            row.right_helix_joint.clicked.connect(self.cell_widget_updated.emit)
            self.setCellWidget(index, 1, row.right_helix_joint)

            # column 2 - theta switch multiple
            row.theta_switch_multiple = TableIntegerBox(
                domain.theta_switch_multiple, minimum=-1
            )
            row.theta_switch_multiple.setEnabled(False)
            self.setCellWidget(index, 2, row.theta_switch_multiple)

            # column 3 - theta interior multiple
            row.theta_interior_multiple = TableIntegerBox(
                domain.theta_interior_multiple,
                show_buttons=True,
                minimum=1,
                maximum=20,
            )
            row.theta_interior_multiple.valueChanged.connect(
                self.cell_widget_updated.emit
            )
            self.setCellWidget(index, 3, row.theta_interior_multiple)

            # column 4 - initial NEMid count
            row.domain_count = TableIntegerBox(domain.count)
            row.domain_count.valueChanged.connect(self.cell_widget_updated.emit)
            self.setCellWidget(index, 4, row.domain_count)

            self.side_headers.append(f"#{index + 1}")

            # append to the main row storage container
            self.rows.append(row)

        class smooth_interior_updating:
            @classmethod
            def surrounding(cls, i):
                # make sure to wrap around to the beginning/end of the domains list
                # if "i" is the length of the list or is 0
                if i == (len(self.rows) - 1):
                    surrounding = (i - 1, i, 0)
                elif i == 0:
                    surrounding = (len(self.rows) - 1, 0, i + 1)
                else:
                    surrounding = (i - 1, i, i + 1)

                surrounding = [
                    self.rows[surrounding[0]].theta_interior_multiple,
                    self.rows[surrounding[1]].theta_interior_multiple,
                    self.rows[surrounding[2]].theta_interior_multiple,
                ]

                return surrounding

            @classmethod
            def down(cls, i):
                surrounding = cls.surrounding(i)
                surrounding[0].setValue(surrounding[0].value() + 1)
                # it was just ticked down 1, so tick it down 1 more
                surrounding[1].setValue(surrounding[1].value() - 1)
                surrounding[2].setValue(surrounding[2].value() + 1)

            @classmethod
            def up(cls, i):
                surrounding = cls.surrounding(i)
                surrounding[0].setValue(surrounding[0].value() - 1)
                # it was just ticked up 1, so tick it up 1 more
                surrounding[1].setValue(surrounding[1].value() + 1)
                surrounding[2].setValue(surrounding[2].value() - 1)

        for index, row in enumerate(self.rows):
            row.theta_interior_multiple.down_button_clicked.connect(
                lambda i=index: smooth_interior_updating.down(i)
            )
            row.theta_interior_multiple.up_button_clicked.connect(
                lambda i=index: smooth_interior_updating.up(i)
            )

        self.setVerticalHeaderLabels(self.side_headers)

    def fetch_domains(self) -> list:
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

            domain = domains.storage.Domain(
                theta_interior_multiple,
                (left_helical_joint, right_helical_joint),
                count,
            )

            domains.append(domain)

        return domains
