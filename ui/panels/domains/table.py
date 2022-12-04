import logging
from types import SimpleNamespace
from typing import Literal, List

from PyQt6.QtCore import pyqtSignal, Qt, QEvent
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtWidgets import (
    QTableWidget,
    QHeaderView,
    QAbstractItemView, QApplication,
)

from constants.directions import *
from structures.domains import Domain, Domains
from structures.profiles import NucleicAcidProfile
from ui.widgets import DirectionalButton, TableIntegerBox

logger = logging.getLogger(__name__)


class Table(QTableWidget):
    """Nucleic Acid Config Tab."""

    helix_joint_updated = pyqtSignal()
    cell_widget_updated = pyqtSignal()

    def __init__(self, parent, nucleic_acid_profile: NucleicAcidProfile) -> None:
        super().__init__(parent)
        # store the nucleic acid profile
        self.nucleic_acid_profile = nucleic_acid_profile

        # header storage areas
        self.side_headers = []
        self.top_headers = []

        # all current row data
        # (domain index = row index)
        self.rows = []

        # set up headers
        self._headers()

        # style the widget
        self._style()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Intercept a keypress to alter tabbing."""
        if event.key() in (
            Qt.Key.Key_Tab,
            Qt.Key.Key_Backtab,
            Qt.Key.Key_Down,
            Qt.Key.Key_Up,
        ):
            row, column = self.currentRow(), self.currentColumn()
            self.cellWidget(row, column).editingFinished.emit()
            self.cell_widget_updated.emit()
            if event.key() in (Qt.Key.Key_Tab, Qt.Key.Key_Down):
                row += 1
            else:
                row -= 1
            if row == len(self.rows):
                row = 0
            self.setTabKeyNavigation(False)
            self.blockSignals(True)
            to_focus = self.cellWidget(row, column)
            if to_focus is not None:
                self.setCurrentCell(row, column)
                to_focus.setFocus()
                for i in range(6):
                    event = QKeyEvent(
                        QEvent.Type.KeyPress,
                        Qt.Key.Key_Right,
                        Qt.KeyboardModifier.NoModifier
                    )
                    QApplication.postEvent(to_focus, event)
            self.blockSignals(False)
            self.setTabKeyNavigation(True)
        else:
            super().keyPressEvent(event)

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

    def dump_domains(self, domains: Domains) -> None:
        """
        Dump a list of domain objects.

        Args:
            domains (List(Domain)): A list of all domains to dump.
        """
        # create rows before we input widgets
        self.setRowCount(domains.subunit.count)

        # clear out the side headers list
        self.side_headers = []

        # container for current row items
        self.rows.clear()

        # insert all domains
        for index, domain in enumerate(domains.subunit.domains):
            # container for currently-being-added widgets
            row = SimpleNamespace()

            # column 0 - left helical joint
            row.left_helix_joint = DirectionalButton(
                self, domains.domains[index].left_helix_joint_direction
            )
            row.left_helix_joint.clicked.connect(self.helix_joint_updated.emit)
            row.left_helix_joint.clicked.connect(self.cell_widget_updated.emit)
            self.setCellWidget(index, 0, row.left_helix_joint)

            # column 1 - right helical joint
            row.right_helix_joint = DirectionalButton(
                self, domains.domains[index].right_helix_joint_direction
            )
            row.right_helix_joint.clicked.connect(self.helix_joint_updated.emit)
            row.right_helix_joint.clicked.connect(self.cell_widget_updated.emit)
            self.setCellWidget(index, 1, row.right_helix_joint)

            # column 2 - theta switch multiple
            row.theta_s_multiple = TableIntegerBox(
                domain.theta_s_multiple, minimum=-1
            )
            row.theta_s_multiple.setEnabled(False)
            self.setCellWidget(index, 2, row.theta_s_multiple)

            # column 3 - theta interior multiple
            row.theta_interior_multiple = TableIntegerBox(
                domain.theta_interior_multiple,
                show_buttons=True,
                minimum=1,
                maximum=30,
            )
            row.theta_interior_multiple.editingFinished.connect(
                self.cell_widget_updated.emit
            )
            self.setCellWidget(index, 3, row.theta_interior_multiple)

            # column 4 - initial NEMid count
            row.domain_count = TableIntegerBox(domain.count)
            row.domain_count.editingFinished.connect(self.cell_widget_updated.emit)
            self.setCellWidget(index, 4, row.domain_count)

            self.side_headers.append(f"#{index + 1}")

            # append to the row storage container
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
                self.cell_widget_updated.emit()

            @classmethod
            def up(cls, i):
                surrounding = cls.surrounding(i)
                surrounding[0].setValue(surrounding[0].value() - 1)
                # it was just ticked up 1, so tick it up 1 more
                surrounding[1].setValue(surrounding[1].value() + 1)
                surrounding[2].setValue(surrounding[2].value() - 1)
                self.cell_widget_updated.emit()

        for index, row in enumerate(self.rows):
            row.theta_interior_multiple.down_button_clicked.connect(
                lambda i=index: smooth_interior_updating.down(i)
            )
            row.theta_interior_multiple.up_button_clicked.connect(
                lambda i=index: smooth_interior_updating.up(i)
            )

        self.setVerticalHeaderLabels(self.side_headers)

    def fetch_domains(self) -> List[Domain]:
        """Obtain a list of the currently chosen domains.

        This returns a list of Domain objects, NOT a Domains object.

        Returns:
            A list of the domains that populate the domains table.
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

            domain = Domain(
                self.nucleic_acid_profile,
                domain,
                theta_interior_multiple,
                left_helical_joint,
                right_helical_joint,
                count,
            )

            domains.append(domain)

        return domains
