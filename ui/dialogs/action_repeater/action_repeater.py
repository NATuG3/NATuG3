from typing import Literal, Type, Iterable

from PyQt6 import uic
from PyQt6.QtCore import pyqtSlot, pyqtSignal
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


class ActionRepeater(QDialog):
    """
    A dialog for repeating an action over many nucleosides.

    Attributes:
        strands: The Strands container that the actions will be enacted on.
        point: The point to enact the action on and continue onwards within its strand.
        point_strand_length: The number of nucleosides in the strand that the point is
            in.
        action: The action to enact.
        nucleic_acid_profile: The NucleicAcidProfile to fetch B from.
        main_form: The main form layout that holds all the form elements.
        button_box: The QDialogButtonBox that holds the "OK" and "Cancel" buttons.
        header_label: The QLabel that holds the header text.
        repeat_for: The QComboBox that holds the number of times to repeat the action
            traveling in the direction of the strand.
        repeat_forever: The QCheckBox that holds the "repeat forever" checkbox,
            which dictates whether to repeat the action forever along the strand.
    """

    updated = pyqtSignal()
    _name = "Action Repeater"

    def __init__(
        self,
        parent,
        action: Literal["conjunct", "link", "unlink", "highlight"],
        point: Point,
        strands: Strands,
        nucleic_acid_profile: NucleicAcidProfile,
        types_to_run_on: tuple[Type],
    ):
        super(ActionRepeater, self).__init__(parent)
        uic.loadUi("ui/dialogs/action_repeater/action_repeater.ui", self)

        self.action = action
        self.point = point
        self.types_to_run_on = types_to_run_on
        self.point_strand_length = len(point.strand.items.by_type(types_to_run_on))
        self.strands = strands
        self.nucleic_acid_profile = nucleic_acid_profile

        self.point.styles.change_state("highlighted")
        self._set_initial_values()
        self._hook_signals()
        self._prettify()

    @classmethod
    def run(cls, *args, **kwargs):
        """
        Run the dialog on a strand.

        Args:
            *args: The arguments to pass to the dialog.
        """
        cls(*args, **kwargs).exec()

    def _set_initial_values(self):
        self.repeat_every.setMaximum(self.point_strand_length)

        if self.action == "conjunct":
            self.repeat_for.setMaximum(
                self.point_strand_length // self.nucleic_acid_profile.B
            )
        else:
            self.repeat_for.setMaximum(self.point_strand_length)

    def _prettify(self):
        """Prettify the ui elements."""
        self.setWindowTitle(f"{self._name} Dialog")
        if self.action == "conjunct":
            self.repeat_for_label.setText("x B NEMids")
        else:
            self.repeat_for_label.setText("NEMids")

    def _on_accepted(self):
        """Run the action on the strand based on the dialog's settings."""
        match self.action:
            case "conjunct":
                repeat_every = self.repeat_every.value() * self.nucleic_acid_profile.B
            case "nick":
                repeat_every = self.repeat_every.value()
            case "unnick":
                repeat_every = self.repeat_every.value()
            case "highlight":
                repeat_every = self.repeat_every.value()
            case _:
                raise ValueError(f"Invalid action: {self.action}")

        assert self.point.strand.strands is self.strands
        self.strands.do_many(
            self.action,
            self.point,
            repeat_every,
            self.repeat_for.value(),
            self.point.strand.items.by_type(self.types_to_run_on),
        )

        self.updated.emit()

    def _on_cancelled(self):
        """Reset the point's state to normal and close the dialog."""
        self.point.styles.change_state("default")
        self.updated.emit()
        self.close()

    def _hook_signals(self):
        self.repeat_forever.stateChanged.connect(self._on_repeat_forever_clicked)
        self.repeat_forever.setChecked(True)
        self.repeat_for.editingFinished.connect(self._on_repeat_for_changed)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.accepted.connect(self._on_accepted)
        self.rejected.connect(self._on_cancelled)

    @pyqtSlot()
    def _on_repeat_for_changed(self):
        if self.repeat_for.value() == 1:
            self.repeat_for.setSuffix(" time")
        else:
            self.repeat_for.setSuffix(" times")

    @pyqtSlot()
    def _on_repeat_forever_clicked(self):
        if self.repeat_forever.isChecked():
            self.repeat_for.setEnabled(False)
            self.repeat_for.setStatusTip("Disabled when repeating forever is checked")
        else:
            self.repeat_for.setEnabled(True)
