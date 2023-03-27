from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QSpinBox,
    QLabel,
    QCheckBox,
    QFormLayout,
    QDialogButtonBox,
)

from structures.profiles import NucleicAcidProfile
from structures.strands import Strands


class ActionRepeaterDialog(QDialog):
    _name = "Action Repeater"

    def __init__(
        self, parent, strands: Strands, nucleic_acid_profile: NucleicAcidProfile
    ):
        super(ActionRepeaterDialog, self).__init__(parent)
        self.strands = strands
        self.nucleic_acid_profile = nucleic_acid_profile

        self.main_form = None
        self.button_box = None
        self.header_label = None
        self.repeat_count = None
        self.repeat_forever = None

        self._setup_ui()

    def _prettify(self):
        """Prettify the ui elements."""
        self.setWindowTitle(f"{self._name} Dialog")

    def _setup_ui(self):
        """Set up all the ui elements."""
        self.setLayout(QVBoxLayout())

        # Create a header label that says what the widget is
        self.header_label = QLabel(self._name)
        self.header_label.setStyleSheet("QLabel{font-size: 16px}")

        # Create the main form area for the settings to go
        self.main_form = QFormLayout()

        # At a spinbox that lets the user choose how many nucleosides to repeat for
        self.repeat_count = QSpinBox()
        self.repeat_count.setRange(1, 99999)
        self.repeat_count.setSuffix(" ")
        self.main_form.addRow("Repeat action every", self.repeat_count)

        # Add a checkbox that lets the user repeat their pattern indefinitely
        self.repeat_forever = QCheckBox()
        self.main_form.addRow("Repeat forever", self.repeat_forever)

        # Add the dialog button box
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )

    def _hook_signals(self):
        self.repeat_forever.clicked.connect(self._on_repeat_forever_clicked)
        self.repeat_forever.setChecked(True)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

    @pyqtSlot()
    def _on_repeat_forever_clicked(self):
        if self.repeat_forever.isChecked():
            self.repeat_count.setEnabled(False)
            self.repeat_count.setStatusTip("Disabled when repeating forever is checked")
        else:
            self.repeat_count.setEnabled(True)
