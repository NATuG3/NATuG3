from functools import partial
from os.path import abspath
from threading import Thread
from typing import Tuple, Type

from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QDialog
from PyQt6 import uic

from natug.structures.points import NEMid, Nucleoside
from natug.ui.plotters import SideViewPlotter, TopViewPlotter, side_view
from natug.ui.widgets.adjustable_padding import AdjustablePadding
from natug.utils import show_in_file_explorer


class PlotExporter(QDialog):
    """
    The plot exporter dialog.

    This dialog allows the user to export the top and side view plots as high resolution
    images (PNG or JPG) or vector graphics (SVG).

    Attributes:
        runner: NATuG's runner.
        side_view_export_plot: The side view plot to export.
        top_view_export_plot: The top view plot to export.

    Methods:
        get_sideview_plot_modifiers: Return the plot modifiers.
        get_sideview_point_types: Return the plot types to export.
    """

    def __init__(self, runner):
        """
        Initialize the plot exporter dialog.

        Args:
            runner: NATuG's runner.
        """
        super().__init__(runner.window)
        self.runner = runner
        self.side_view_export_plot = None
        self.top_view_export_plot = None
        uic.loadUi("./ui/dialogs/plot_exporter/plot_exporter.ui", self)

        self._side_view_plot_area()
        self._top_view_plot_area()
        self._hook_signals()
        self._prettify()

    def get_sideview_plot_modifiers(self):
        """Return the plot modifiers."""
        return side_view.PlotModifiers(
            nick_mod=self.nick_size_modifier.value(),
            nucleoside_mod=self.nucleoside_size_modifier.value(),
            NEMid_mod=self.NEMid_size_modifier.value(),
            point_outline_mod=self.point_outline_modifier.value(),
            stroke_mod=self.strand_stroke_modifier.value(),
            gridline_mod=self.gridline_width_modifier.value(),
        )

    def get_sideview_point_types(self) -> Tuple[Type, ...]:
        """Return the plot types to export."""
        plot_types = []
        if self.plot_NEMids.isChecked():
            plot_types.append(NEMid)
        if self.plot_nucleosides.isChecked():
            plot_types.append(Nucleoside)
        return tuple(plot_types)

    def _prettify(self):
        """Prettify the dialog."""
        # Get the screen size
        screen = self.runner.application.primaryScreen().geometry()
        screen_width, screen_height = (
            screen.width(),
            screen.height(),
        )
        desired_width, desired_height = (
            round(screen_width * 0.85),
            round(screen_height * 0.8),
        )
        x, y = (
            round((screen_width - desired_width) / 2),
            round((screen_height - desired_height) / 2),
        )

        # Resize the dialog to fill the screen
        self.setGeometry(x, y, desired_width, desired_height)
        self.setFixedWidth(desired_width)
        self.setFixedHeight(desired_height)

    def _side_view_plot_area(self):
        """Set up the side view preview plot area."""
        self.side_view_export_plot = SideViewPlotter(
            strands=self.runner.managers.strands.current,
            double_helices=self.runner.managers.double_helices.current,
            domains=self.runner.managers.domains.current,
            nucleic_acid_profile=self.runner.managers.nucleic_acid_profile.current,
            point_types=self.get_sideview_point_types(),
            modifiers=self.get_sideview_plot_modifiers(),
            title=self.side_view_plot_title.text(),
            padding=self.side_view_padding.value(),
            dot_hidden_points=False,
            show_unstable_helix_joints=self.plot_unstable_joint_indicators.isChecked(),
        )
        self.side_view_export_plot.setStyleSheet("border: 2px solid black;")
        self.side_view_plot_area.layout().insertWidget(
            0, AdjustablePadding(self, self.side_view_export_plot)
        )

    def _top_view_plot_area(self):
        self.top_view_export_plot = TopViewPlotter(
            domains=self.runner.managers.domains.current,
            circle_radius=self.runner.managers.nucleic_acid_profile.current.D,
            plot_buttons=False,
            numbers=self.top_view_numbers.isChecked(),
            rotation=self.top_view_rotation.value(),
            padding=self.top_view_padding.value(),
            stroke=self.top_view_stroke.value(),
            title=self.top_view_plot_title.text(),
        )
        self.top_view_export_plot.setStyleSheet("border: 2px solid black;")
        self.top_view_plot_area.layout().insertWidget(
            0, AdjustablePadding(self, self.top_view_export_plot)
        )

    def _hook_signals(self):
        """Hook all the signals."""
        self.cancel_export.clicked.connect(self.reject)
        self.export_plots.clicked.connect(self.accept)
        self.accepted.connect(self._on_export_plots_clicked)

        # Hook all the side view signals
        for input_ in (
            self.nick_size_modifier,
            self.nucleoside_size_modifier,
            self.NEMid_size_modifier,
            self.point_outline_modifier,
            self.strand_stroke_modifier,
            self.gridline_width_modifier,
            self.side_view_padding,
            self.side_view_plot_title,
        ):
            input_.editingFinished.connect(self.update_side_view_preview)

        for input_ in (
            self.plot_NEMids,
            self.plot_nucleosides,
            self.plot_unstable_joint_indicators,
        ):
            input_.stateChanged.connect(self.update_side_view_preview)

        # When the side view padding is changed re-autorange the plot
        self.side_view_padding.valueChanged.connect(
            self.side_view_export_plot.auto_range
        )

        # Hook all the top view signals
        for input_ in (
            self.top_view_rotation,
            self.top_view_plot_title,
            self.top_view_stroke,
            self.top_view_padding,
        ):
            input_.editingFinished.connect(self.update_top_view_preview)
        self.top_view_numbers.stateChanged.connect(self.update_top_view_preview)
        self.top_view_padding.valueChanged.connect(self.top_view_export_plot.autoRange)

    @pyqtSlot()
    def update_side_view_preview(self):
        """Update the sideview preview plot."""
        self.side_view_export_plot.modifiers = self.get_sideview_plot_modifiers()
        self.side_view_export_plot.title = self.side_view_plot_title.text()
        self.side_view_export_plot.point_types = self.get_sideview_point_types()
        self.side_view_export_plot.padding = self.side_view_padding.value()
        self.side_view_export_plot.plot()

    @pyqtSlot()
    def update_top_view_preview(self):
        """Update the topview preview plot."""
        self.top_view_export_plot.title = self.top_view_plot_title.text()
        self.top_view_export_plot.numbers = self.top_view_numbers.isChecked()
        self.top_view_export_plot.rotation = self.top_view_rotation.value()
        self.top_view_export_plot.padding = self.top_view_padding.value()
        self.top_view_export_plot.stroke = self.top_view_stroke.value()
        self.top_view_export_plot.refresh()

    @pyqtSlot()
    def _on_export_plots_clicked(self):
        """Export the plots."""
        top_view_export_filename = (
            f"saves/{self.top_view_filename.text()}"
            f"{self.top_view_filetype.currentText().lower()}"
        )
        side_view_export_filename = (
            f"saves/{self.side_view_filename.text()}"
            f"{self.side_view_filetype.currentText().lower()}"
        )

        side_view_exporter = partial(
            self.side_view_export_plot.export, side_view_export_filename, False
        )
        top_view_exporter = partial(
            self.top_view_export_plot.export, top_view_export_filename, False
        )

        threads = (
            Thread(target=side_view_exporter),
            Thread(target=top_view_exporter),
        )
        [thread.start() for thread in threads]
        [thread.join() for thread in threads]
        show_in_file_explorer(abspath("save"))
