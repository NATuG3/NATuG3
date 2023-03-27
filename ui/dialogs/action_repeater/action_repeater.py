from typing import Literal

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QSpinBox,
    QLabel,
    QCheckBox,
    QFormLayout,
    QDialogButtonBox,
    QHBoxLayout,
    QComboBox,
)

from constants.directions import UP, UP_DOWN, DOWN
from structures.points import Nucleoside
from structures.points.point import Point
from structures.profiles import NucleicAcidProfile
from structures.strands import Strands


class ActionRepeaterDialog(QDialog):
    """
    A dialog for repeating an action over many nucleosides.

    Attributes:
        strands: The Strands container that the actions will be enacted on.
        point: The point to enact the action on and continue onwards within its strand.
        point_strand_length: The number of nucleosides in the strand that the point is
            in.
        action: The action to enact.
        replot: The replot function to call for refreshing the plot.
        nucleic_acid_profile: The NucleicAcidProfile to fetch B from.
        main_form: The main form layout that holds all the form elements.
        button_box: The QDialogButtonBox that holds the "OK" and "Cancel" buttons.
        header_label: The QLabel that holds the header text.
        repeat_for: The QComboBox that holds the number of times to repeat the action
            traveling in the direction of the strand.
        repeat_forever: The QCheckBox that holds the "repeat forever" checkbox,
            which dictates whether to repeat the action forever along the strand.
    """

    _name = "Action Repeater"

    def __init__(
        self,
        parent,
        action,
        replot,
        point,
        strands: Strands,
        nucleic_acid_profile: NucleicAcidProfile,
    ):
        super(ActionRepeaterDialog, self).__init__(parent)
        self.action = action
        self.replot = replot
        self.point = point
        self.point_strand_length = len(self.point.strand.items.by_type(Nucleoside))
        self.strands = strands
        self.nucleic_acid_profile = nucleic_acid_profile

        self.point.styles.change_state("highlighted")
        self.replot()

        self.main_form = None
        self.button_box = None
        self.header_label = None
        self.repeat_for = None
        self.repeat_forever = None

        self._setup_ui()

    @classmethod
    def run(cls, *args, **kwargs):
        """
        Run the dialog on a strand.

        Args:
            *args: The arguments to pass to the dialog.
        """
        dialog = cls(*args, **kwargs)
        dialog.exec()

    def _prettify(self):
        """Prettify the ui elements."""
        self.setWindowTitle(f"{self._name} Dialog")

    def _setup_ui(self):
        """Set up all the ui elements."""
        self.setLayout(QVBoxLayout())

        # Create a header label that says what the widget is
        self.header_label = QLabel(self._name)
        self.header_label.setStyleSheet("QLabel{font-size: 16px}")

        # Create a layout that will hold the main form elements
        self.main_form = QVBoxLayout()

        # Create a layout that will hold the repeat count and direction
        self.repeat_every = QSpinBox()
        self.repeat_every.setMinimum(1)
        self.repeat_every.setMaximum(self.point_strand_length)
        self.repeat_every.setValue(1)
        self.repeat_every.setSuffix("·B nucleosides")
        repeat_every_area = QHBoxLayout()
        repeat_every_area.addWidget(QLabel("Repeat action repeat_every"))
        repeat_every_area.addWidget(self.repeat_every)
        self.main_form.addLayout(repeat_every_area)

        # Create the layout that will hold how many repetitions that they want
        self.repeat_for = QSpinBox()
        self.repeat_for.setMinimum(1)
        self.repeat_for.setMaximum(
            self.point.strand.items.by_type(Point)//self.nucleic_acid_profile.B
        )
        repeat_count_area = QHBoxLayout()
        repeat_count_area.addWidget(QLabel("Repeat action for"))

        # Add a checkbox that lets the user repeat their pattern indefinitely
        self.repeat_forever = QCheckBox("Repeat forever")
        self.main_form.addWidget(self.repeat_forever)

        # Add the dialog button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

    def _on_accepted(self):
        """Run the action on the strand based on the dialog's settings."""
        if self.repeat_forever.isChecked():
            repeat_every = None
        else:
            repeat_every = self.repeat_for.value() * self.nucleic_acid_profile.B

        self.strands.do_many(
            self.action,
            self.point,
            repeat_every,
            self.repeat_for.value()
        )

    def _hook_signals(self):
        self.repeat_forever.clicked.connect(self._on_repeat_forever_clicked)
        self.repeat_forever.setChecked(True)
        self.repeat_for.editingFinished.connect(self._on_repeat_for_changed)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.accepted.connect(self._on_accepted)

    @pyqtSlot()
    def _on_repeat_for_changed(self):
        self.repeat_every.setMaximum(
            # When the repeat repeat_every is changed the repeat for becomes the repeat repeat_every
            self.repeat_for.value()
        )

    @pyqtSlot()
    def _on_repeat_forever_clicked(self):
        if self.repeat_forever.isChecked():
            self.repeat_for.setEnabled(False)
            self.repeat_for.setStatusTip("Disabled when repeating forever is checked")
        else:
            self.repeat_for.setEnabled(True)
