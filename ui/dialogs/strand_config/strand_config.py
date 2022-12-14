import atexit

from PyQt6 import uic
from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtGui import QBrush, QColor
from PyQt6.QtWidgets import QDialog, QColorDialog, QGraphicsScene

from structures.strands import Strand
from ui.dialogs.sequence_editor.display_area import SequenceDisplayArea
from ui.dialogs.sequence_editor.sequence_editor import SequenceEditor


class StrandConfig(QDialog):
    updated = pyqtSignal()

    max_thickness = 50

    def __init__(self, parent, strand: Strand):
        super().__init__(parent)
        uic.loadUi("ui/dialogs/strand_config/strand_config.ui", self)

        self.strand = strand
        self.setWindowTitle(
            f"Strand #{self.strand.parent.index(self.strand) + 1} Config"
        )
        self._sequencing()
        self._color_selector()
        self._thickness_selector()
        self._strand_params()

        self.strand.highlighted = True

        self.finished.connect(self.when_finished)
        atexit.register(self.when_finished)

    def when_finished(self) -> None:
        self.strand.highlighted = False
        self.updated.emit()

    def _strand_params(self):
        """Setup parameters based on strand parameters."""
        self.NEMids_in_strand.setValue(len(self.strand.NEMids()))
        self.nucleosides_in_strand.setValue(len(self.strand.NEMids()))
        self.closed.setChecked(self.strand.closed)
        self.empty.setChecked(self.strand.empty)

        if self.strand.thickness > self.max_thickness:
            thickness = 99
        else:
            thickness = (self.strand.thickness) * 99 / self.max_thickness

        thickness = round(thickness)
        self.thickness.setValue(thickness)

    def _sequencing(self):
        """Set up the sequencing area."""

        # add the sequencing display area
        self.sequence_display = SequenceDisplayArea(None, self.strand.sequence)
        self.sequencing_area.layout().insertWidget(0, self.sequence_display)

        def sequencing_editor_clicked():
            """Worker for when 'sequence editor' is clicked."""
            self.strand.sequence = SequenceEditor.fetch_sequence(
                self.parent(), self.strand.sequence
            )
            self.sequence_display.bases = self.strand.sequence
            self.updated.emit()

        self.sequence_editor.clicked.connect(sequencing_editor_clicked)

    def _color_selector(self):
        """Set up the color selector."""

        # set up the color preview box
        self.color_preview.setScene(QGraphicsScene())

        def update_color_preview():
            """Update the color preview box to the current strand color."""
            self.color_preview.scene().setBackgroundBrush(
                QBrush(QColor(*self.strand.color))
            )

        # strand color could change for many reasons other than them using the color selector
        # so for ease we will just automatically update the preview box every .1 seconds with
        # the current strand color (this is an unideal solution, but it works perfectly fine)
        update_color_preview()
        update_color_looper = QTimer(self)
        update_color_looper.timeout.connect(update_color_preview)
        update_color_looper.start(100)

        def color_chooser_clicked():
            """Worker for when the color chooser box is clicked."""
            self.auto_color.setChecked(False)
            self.strand.color = QColorDialog.getColor().getRgb()
            self.strand.auto_color = False
            update_color_preview()
            self.updated.emit()

        self.color_chooser.clicked.connect(color_chooser_clicked)

        # update the auto color checkbox to the current state of the strand
        self.auto_color.setChecked(self.strand.auto_color)

        def auto_color_checked(checked):
            """Worker for when the auto color checkbox is clicked."""
            if checked:
                self.strand.auto_color = True
            else:
                self.strand.auto_color = False
            self.updated.emit()

        self.auto_color.stateChanged.connect(auto_color_checked)

    def _thickness_selector(self):
        """Set up the thickness selector."""

        def slider_to_thickness():
            """Map the thickness slider to the strand thickness."""
            return int((self.thickness.value() * self.max_thickness) / 99)

        def thickness_to_slider():
            """Map the strand thickness to the thickness slider."""
            return int((self.strand.thickness * 99) / self.max_thickness)

        def thickness_changed():
            """Worker for when the thickness slider is changed."""
            self.auto_thickness.setChecked(False)
            self.strand.thickness = slider_to_thickness()
            self.updated.emit()

        self.thickness.valueChanged.connect(thickness_changed)

        # update the thickness based on the current strand's thickness
        self.auto_thickness.setChecked(self.strand.auto_thickness)

        def auto_thickness_checked(checked):
            """Worker for when the auto thickness checkbox is checked."""
            if checked:
                self.strand.auto_thickness = True
            else:
                self.strand.thickness = slider_to_thickness()
            self.updated.emit()

        self.auto_thickness.stateChanged.connect(auto_thickness_checked)

        def auto_thickness_updater():
            self.thickness.blockSignals(True)
            self.thickness.setValue(thickness_to_slider())
            self.thickness.blockSignals(False)

        update_thickness_looper = QTimer(self)
        update_thickness_looper.timeout.connect(auto_thickness_updater)
        update_thickness_looper.start(100)
