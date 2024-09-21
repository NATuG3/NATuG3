from dataclasses import dataclass
from typing import Callable, List, Tuple

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QDoubleSpinBox, QTabWidget

from natug.structures.domains import Domain
from natug.structures.profiles import NucleicAcidProfile
from natug.ui.config.tabs.domains.tables.angles import DomainsAnglesTable
from natug.ui.config.tabs.domains.tables.counts import DomainsCountsTable
from natug.ui.widgets import DirectionalButton, TableIntegerBox
from natug.ui.widgets.triple_spinbox import TripleSpinbox


@dataclass(slots=True)
class RowWidgets:
    """
    A container for storing table data.

    Attributes:
        theta_m_multiple: User settable theta m multiple.
        theta_s_multiple: Automatically computed switch angle multiple.
        theta_i: The actual interior angle. Theta_c * theta_m_multiple.
        left_helix_joint: User settable left helix joint direction.
        right_helix_joint: User settable right helix joint direction.
        up_helix_count: User settable values for the bottom, middle, and top of the
            left helical strand.
        down_helix_count: User settable values for the bottom, middle, and top of the
            right helical strand.
    """

    theta_m_multiple: TableIntegerBox = None
    theta_i: QDoubleSpinBox = None
    theta_s_multiple: TableIntegerBox = None
    left_helix_joint: DirectionalButton = None
    right_helix_joint: DirectionalButton = None
    up_helix_count: TripleSpinbox = None
    down_helix_count: TripleSpinbox = None

    def to_domain(self, nucleic_acid_profile: NucleicAcidProfile):
        """Obtain a domain object from the data in the RowWidgets."""
        return Domain(
            nucleic_acid_profile=nucleic_acid_profile,
            theta_m_multiple=self.theta_m_multiple.value(),
            left_helix_joint=self.left_helix_joint.state,
            right_helix_joint=self.right_helix_joint.state,
            up_helix_count=self.up_helix_count.values(),
            down_helix_count=self.down_helix_count.values(),
        )


class SmoothInteriorUpdating:
    """
    Automatic theta_m arrow click adjacent adjustments.

    Attributes:
        rows (List(RowWidgets)): A list of all rows in the table.
        signal (Callable): A signal to release when the value of a box changes.
    """

    def __init__(self, rows, signal: Callable):
        self.rows = rows
        self.signal = signal

    def surrounding(self, i):
        # make sure to wrap around to the beginning/end of the domains list
        # if "i" is the length of the list or is 0
        if i == (len(self.rows) - 1):
            surrounding = (i - 1, i, 0)
        elif i == 0:
            surrounding = (len(self.rows) - 1, 0, i + 1)
        else:
            surrounding = (i - 1, i, i + 1)

        surrounding = [
            self.rows[surrounding[0]].theta_m_multiple,
            self.rows[surrounding[1]].theta_m_multiple,
            self.rows[surrounding[2]].theta_m_multiple,
        ]

        return surrounding

    def down(self, i):
        surrounding = self.surrounding(i)
        surrounding[0].setValue(surrounding[0].value() + 1)
        # It was just ticked down 1, so tick it down 1 more
        surrounding[1].setValue(surrounding[1].value() - 1)
        surrounding[2].setValue(surrounding[2].value() + 1)
        # Release a signal since the value has changed
        self.signal()

    def up(self, i):
        surrounding = self.surrounding(i)
        surrounding[0].setValue(surrounding[0].value() - 1)
        # it was just ticked up 1, so tick it up 1 more
        surrounding[1].setValue(surrounding[1].value() + 1)
        surrounding[2].setValue(surrounding[2].value() - 1)
        # Release a signal since the value has changed
        self.signal()


class DomainsTablesArea(QTabWidget):
    """
    The area for the tables in the domains tab.

    Attributes:
        nucleic_acid_profile (NucleicAcidProfile): The nucleic acid profile to use.

    Signals:
        cell_widget_updated: A signal to release when a cell widget is updated.
        helix_joint_updated: A signal to release when a helix joint is updated.
        triple_spinbox_updated: A signal to release when a triple spinbox is updated.
    """

    cell_widget_updated = pyqtSignal()
    helix_joint_updated = pyqtSignal()
    triple_spinbox_updated = pyqtSignal(tuple)

    def __init__(self, parent, nucleic_acid_profile: NucleicAcidProfile) -> None:
        super().__init__(parent)
        self.nucleic_acid_profile = nucleic_acid_profile
        self.rows = []

        self.angles_table = None
        self.angles_tab = None
        self._angles_tab()

        self.counts_table = None
        self.counts_tab = None
        self._counts_tab()

        self._hook_signals()

    def dump_domains(self, domains: List[Domain]) -> None:
        """
        Dump a list of domain objects.

        This dumps a list of Domain objects rather than a Domains object. It does not
        include symmetry, and is just a raw list of domains.

        Args:
            domains (List(Domain)): A list of all domains to dump.
        """
        # Create rows before we input widgets
        self.angles_table.setRowCount(len(domains))
        self.counts_table.setRowCount(len(domains))

        # Clear the row widget container
        self.rows.clear()

        # Array for the index labels that go to the left of the table
        side_headers = []

        # insert all domains
        for index, domain in enumerate(domains):
            # Container for currently-being-added widgets
            row = RowWidgets()

            # Angles Table, Column 0 - left helical joint
            row.left_helix_joint = DirectionalButton(
                self, domains[index].left_helix_joint
            )
            row.left_helix_joint.clicked.connect(self.helix_joint_updated.emit)
            row.left_helix_joint.clicked.connect(self.cell_widget_updated.emit)
            self.angles_table.setCellWidget(index, 0, row.left_helix_joint)

            # Angles Table, Column 1 - right helical joint
            row.right_helix_joint = DirectionalButton(
                self, domains[index].right_helix_joint
            )
            row.right_helix_joint.clicked.connect(self.helix_joint_updated.emit)
            row.right_helix_joint.clicked.connect(self.cell_widget_updated.emit)
            self.angles_table.setCellWidget(index, 1, row.right_helix_joint)

            # Angles Table, Column 2 - theta switch multiple
            row.theta_s_multiple = TableIntegerBox(domain.theta_s_multiple, minimum=-1)
            row.theta_s_multiple.setEnabled(False)
            self.angles_table.setCellWidget(index, 2, row.theta_s_multiple)

            # Angles Table, Column 3 - theta interior multiple
            row.theta_m_multiple = TableIntegerBox(
                domain.theta_m_multiple,
                show_buttons=True,
                minimum=-999999,
                maximum=999999,
            )
            row.theta_m_multiple.editingFinished.connect(self.cell_widget_updated.emit)
            self.angles_table.setCellWidget(index, 3, row.theta_m_multiple)

            # Angles Table, Column 5 - theta interior
            row.theta_i = QDoubleSpinBox()
            row.theta_i.setRange(0, 9999)
            row.theta_i.setDecimals(2)
            row.theta_i.setValue(domain.theta_i)
            row.theta_i.setEnabled(False)
            row.theta_i.setSuffix("°")
            self.angles_table.setCellWidget(index, 4, row.theta_i)

            # Counts Table, Column 0 - initial NEMid count for the up helix
            row.up_helix_count = TripleSpinbox(domain.up_helix_count)
            row.up_helix_count.editingFinished.connect(
                lambda widget=row.up_helix_count: self.triple_spinbox_updated.emit(
                    widget.values()
                )
            )
            row.up_helix_count.editingFinished.connect(self.cell_widget_updated.emit)
            self.counts_table.setCellWidget(index, 0, row.up_helix_count)

            # Counts Table, Column 1 - initial NEMid count for the down helix
            row.down_helix_count = TripleSpinbox(domain.down_helix_count)
            row.down_helix_count.editingFinished.connect(
                lambda widget=row.down_helix_count: self.triple_spinbox_updated.emit(
                    widget.values()
                )
            )
            row.down_helix_count.editingFinished.connect(self.cell_widget_updated.emit)
            self.counts_table.setCellWidget(index, 1, row.down_helix_count)

            # Store the index label that will be added to the left labels later
            side_headers.append(f"#{index + 1}")

            # append to the row storage container
            self.rows.append(row)

        smooth_interior_updating = SmoothInteriorUpdating(
            self.rows, self.cell_widget_updated.emit
        )

        def modulo_theta_m_upon_change(widget):
            widget.setValue(widget.value() % self.nucleic_acid_profile.B)

        for index, row in enumerate(self.rows):
            row.theta_m_multiple.editingFinished.connect(
                lambda widget=row.theta_m_multiple: modulo_theta_m_upon_change(widget)
            )
            row.theta_m_multiple.down_button_clicked.connect(
                lambda i=index: smooth_interior_updating.down(i)
            )
            row.theta_m_multiple.up_button_clicked.connect(
                lambda i=index: smooth_interior_updating.up(i)
            )

        for table in self.angles_table, self.counts_table:
            table.setVerticalHeaderLabels(side_headers)

    def fetch_domains(self) -> List[Domain]:
        """
        Obtain a list of the currently chosen domains.

        This returns a list of Domain objects, NOT a Domains object.

        Returns:
            A list of the domains that populate the domains table.
        """
        domains = []  # Output list of domains
        for row in self.rows:
            domains.append(row.to_domain(self.nucleic_acid_profile))
        return domains

    def _hook_signals(self):
        """Hook up signals to slots."""
        self.triple_spinbox_updated.connect(self._on_triple_spinbox_updated)

    def _angles_tab(self):
        """Set up the angles tab."""
        self.angles_table = DomainsAnglesTable(self, self.nucleic_acid_profile)
        self.angles_tab = self.addTab(self.angles_table, "Angles")

    def _counts_tab(self):
        """Set up the counts tab."""
        self.counts_table = DomainsCountsTable(self)
        self.counts_tab = self.addTab(self.counts_table, "Counts")

    def _on_triple_spinbox_updated(self, values: Tuple[int, int, int]):
        """
        If a helix count triple spinbox is updated, update all other selected
        cells' values to match.
        """
        selected_triple_spinboxes = []
        ranges = self.counts_table.selectedRanges()
        for r in ranges:
            for row in range(r.topRow(), r.bottomRow() + 1):
                for col in range(r.leftColumn(), r.rightColumn() + 1):
                    item = self.counts_table.cellWidget(row, col)
                    if item is not None:
                        selected_triple_spinboxes.append(item)
        for triple_spinbox in selected_triple_spinboxes:
            triple_spinbox.setValues(values)
