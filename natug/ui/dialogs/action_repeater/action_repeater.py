from PyQt6.QtCore import pyqtSignal, pyqtSlot
from PyQt6.QtWidgets import QDialog
from PyQt6 import uic

from natug.structures.profiles import NucleicAcidProfile
from natug.structures.profiles.action_repeater_profile import ActionRepeaterProfile
from natug.structures.strands import Strands


class ActionRepeaterDialog(QDialog):
    """
    A dialog for repeating an action over many nucleosides.

    Attributes:
        strands: The Strands container that the actions will be enacted on.
        point: The point to enact the action on and continue onwards within its strand.
        point_strand_length: The number of nucleosides in the strand that the point is
            in.
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
        strands: Strands,
        nucleic_acid_profile: NucleicAcidProfile,
    ) -> None:
        """
        Initialize the dialog.

        Args:
            parent: The parent widget.
            strands: The Strands container that the actions will be enacted on.
            nucleic_acid_profile: The NucleicAcidProfile to fetch B from.
        """
        super(ActionRepeaterDialog, self).__init__(parent)
        uic.loadUi("./ui/dialogs/action_repeater/action_repeater.ui", self)

        self.strands = strands
        self.nucleic_acid_profile = nucleic_acid_profile

        self._hook_signals()
        self._prettify()

    @classmethod
    def run(cls, *args, **kwargs) -> None:
        """
        Run the dialog on a strand.

        Args:
            *args: The arguments to pass to the dialog.
        """
        cls(*args, **kwargs).exec()

    def fetch_profile(self) -> ActionRepeaterProfile:
        """
        Fetch the profile from the dialog's settings.

        Returns:
            The profile.
        """
        if self.repeat_every_unit.currentText() == "xB NEMids":
            repeat_every_multiplier = self.nucleic_acid_profile.B * 2
        else:
            repeat_every_multiplier = 1

        if self.repeat_forever.isChecked():
            repeat_for = None
        else:
            repeat_for = self.repeat_for.value()

        return ActionRepeaterProfile(
            repeat_every=self.repeat_every.value(),
            repeat_every_multiplier=repeat_every_multiplier,
            repeat_for=repeat_for,
            bidirectional=self.bidirectional.isChecked(),
            strands=self.strands,
        )

    def dump_profile(self, profile: ActionRepeaterProfile) -> None:
        """
        Dump the profile's settings into the dialog.

        Args:
            profile: The profile to dump.
        """
        self.repeat_every.setValue(profile.repeat_every)
        self.repeat_for.setValue(profile.repeat_for)
        self.bidirectional.setChecked(profile.bidirectional)
        self.repeat_forever.setChecked(profile.repeat_for is None)

    def _prettify(self) -> None:
        """Prettify the ui elements."""
        self.setWindowTitle(f"{self._name} Dialog")

    def _hook_signals(self) -> None:
        self.repeat_forever.stateChanged.connect(self._on_repeat_forever_clicked)
        self.repeat_forever.setChecked(True)
        self.bidirectional.stateChanged.connect(self._on_bidirectional_clicked)
        self.repeat_for.editingFinished.connect(self._on_repeat_for_changed)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    @pyqtSlot()
    def _on_repeat_for_changed(self) -> None:
        if self.repeat_for.value() == 1:
            self.repeat_for.setSuffix(" time")
        else:
            self.repeat_for.setSuffix(" times")

    @pyqtSlot()
    def _on_repeat_forever_clicked(self) -> None:
        if self.repeat_forever.isChecked():
            self.repeat_for.setEnabled(False)
            self.repeat_for.setStatusTip("Disabled when repeating forever is checked")
        else:
            self.repeat_for.setEnabled(True)

    @pyqtSlot()
    def _on_bidirectional_clicked(self) -> None:
        if self.bidirectional.isChecked():
            self.repeat_forever.setText("To ends")
        else:
            self.repeat_forever.setText("To end")
