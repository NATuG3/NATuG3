import logging
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QTableWidget, QHeaderView
from copy import deepcopy
import config.domains.storage
from config.domains.widgets import *
from constants.directions import *
from types import SimpleNamespace

logger = logging.getLogger(__name__)


class Table(QTableWidget):
    """Nucleic Acid Config Tab."""

    def __init__(self, parent) -> None:
        super().__init__()
        self.rows = None
        self.parent = parent

        self.setStyleSheet("QTableView::item{padding: 5px; text-align: center}")

        # self.setShowGrid(False)

        self.top_headers = ("left", "right", "s", "m", "count")
        self.setColumnCount(len(self.top_headers))

        self.setHorizontalHeaderLabels(self.top_headers)

        # dump the domains of the previous save
        self.dump_domains(config.domains.storage.current)

        for i in range(2):
            self.setColumnWidth(i, 35)
            self.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeMode.Fixed
            )

        for i in range(2, 6):
            self.horizontalHeader().setSectionResizeMode(
                i, QHeaderView.ResizeMode.Stretch
            )

    def dump_domains(self, domains_list: list) -> None:
        """Dump a list of domain objects."""
        self.setRowCount(len(domains_list))

        self.side_headers = []
        rows = self.rows = []

        for index, domain in enumerate(domains_list):
            row = SimpleNamespace()

            # column 0 - left helical joint
            row.left_helical_joint = DirectionalButton(self, domain.helix_joints[LEFT])
            self.setCellWidget(index, 0, row.left_helical_joint)

            # column 1 - right helical joint
            row.right_helical_joint = DirectionalButton(
                self, domain.helix_joints[RIGHT]
            )
            self.setCellWidget(index, 1, row.right_helical_joint)

            # column 2 - theta switch multiple
            row.theta_switch_multiple = StyledSpinBox(domain.theta_switch_multiple)
            row.theta_switch_multiple.setEnabled(False)
            self.setCellWidget(index, 2, row.theta_switch_multiple)

            # column 3 - theta interior multiple
            row.theta_interior_multiple = StyledSpinBox(domain.theta_interior_multiple)
            self.setCellWidget(index, 3, row.theta_interior_multiple)

            # column 4 - initial NEMid count
            row.theta_switch_multiple = StyledSpinBox(domain.count)
            row.theta_switch_multiple.setEnabled(False)
            self.setCellWidget(index, 4, row.theta_switch_multiple)

            rows.append(row)
            self.side_headers.append(f"Domain #{index}")

        self.setVerticalHeaderLabels(self.side_headers)


class Panel(QWidget):
    """Nucleic Acid Config Tab."""

    def __init__(self) -> None:
        super().__init__()

        # load in the panel's designer UI
        uic.loadUi("config/domains/panel.ui", self)

        self.table = Table(self)
        self.layout().addWidget(self.table)
