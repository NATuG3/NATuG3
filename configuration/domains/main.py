import logging
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QTableWidget, QHeaderView, QAbstractItemView
import configuration.domains.storage
from configuration.domains.widgets import *
from constants.directions import *
import helpers
from resources.workers import fetch_icon

logger = logging.getLogger(__name__)


class Panel(QWidget):
    """Nucleic Acid Config Tab."""

    def __init__(self) -> None:
        super().__init__()

        # load in the panel's designer UI
        uic.loadUi("configuration/domains/panel.ui", self)

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

    def refresh(self):
        configuration.domains.storage.current.subunit.count = self.subunit_count.value()
        configuration.domains.storage.current.symmetry = self.symmetry.value()

        # update total count (=subunit_count*symmetry)
        self.total_count.setValue(configuration.domains.storage.current.count)

        # update domains table
        self.table.dump_domains(configuration.domains.storage.current.subunit.domains)


class Table(QTableWidget):
    """Nucleic Acid Config Tab."""

    def __init__(self, parent) -> None:
        super().__init__()
        # header storage areas
        self.side_headers = []
        self.top_headers = []

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

    def dump_domains(self, domains_list: list) -> None:
        """Dump a list of domain objects."""

        # create rows before we input widgets
        self.setRowCount(len(domains_list))

        # clear out the side headers list
        self.side_headers = []

        # insert all domains
        for index, domain in enumerate(domains_list):
            # column 0 - left helical joint
            widget = DirectionalButton(self, domain.helix_joints[LEFT])
            widget.clicked.connect(self.cell_value_changed)
            self.setCellWidget(index, 0, widget)

            # column 1 - right helical joint
            widget = DirectionalButton(self, domain.helix_joints[RIGHT])
            widget.clicked.connect(self.cell_value_changed)
            self.setCellWidget(index, 1, widget)

            # column 2 - theta switch multiple
            widget = TableIntegerBox(domain.theta_switch_multiple)
            widget.setEnabled(False)
            widget.valueChanged.connect(self.cell_value_changed)
            self.setCellWidget(index, 2, widget)

            # column 3 - theta interior multiple
            widget = TableIntegerBox(domain.theta_interior_multiple, show_buttons=True)
            widget.valueChanged.connect(self.cell_value_changed)
            self.setCellWidget(index, 3, widget)

            # column 4 - initial NEMid count
            widget = TableIntegerBox(domain.count)
            widget.valueChanged.connect(self.cell_value_changed)
            self.setCellWidget(index, 4, widget)

            self.side_headers.append(f"#{index + 1}")

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

    def cell_value_changed(self):
        """Called whenever a cell's value changes"""
        self.parent.refresh()
