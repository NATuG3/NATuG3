from typing import Tuple, Type

from PyQt6 import uic
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtWidgets import QDialog, QFileDialog

from structures.points import Nucleoside, NEMid
from ui.plotters import SideViewPlotter, side_view, TopViewPlotter
from ui.widgets.adjustable_padding import AdjustablePadding


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
        uic.loadUi("ui/dialogs/plot_exporter/plot_exporter.ui", self)
        self.cancel_export.clicked.connect(self.reject)
        self.export_plots.clicked.connect(self.accept)

        self._hook_signals()
        self._side_view_plot_area()
        self._top_view_plot_area()

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

    def _side_view_plot_area(self):
        """Set up the side view preview plot area."""
        self.side_view_export_plot = SideViewPlotter(
            strands=self.runner.managers.strands.current,
            domains=self.runner.managers.domains.current,
            nucleic_acid_profile=self.runner.managers.nucleic_acid_profile.current,
            point_types=self.get_sideview_point_types(),
            modifiers=self.get_sideview_plot_modifiers(),
            title=self.side_view_plot_title.text(),
        )
        self.side_view_export_plot.setStyleSheet("border: 2px solid black;")
        self.side_view_plot_area.layout().insertWidget(
            0, AdjustablePadding(self, self.side_view_export_plot)
        )

    def _top_view_plot_area(self):
        self.top_view_export_plot = TopViewPlotter(
            domains=self.runner.managers.domains.current,
            domain_radius=self.runner.managers.nucleic_acid_profile.current.D,
            numbers=self.top_view_numbers.isChecked(),
            rotation=self.top_view_rotation.value(),
            title=self.top_view_plot_title.text(),
        )
        self.top_view_export_plot.setStyleSheet("border: 2px solid black;")
        self.top_view_plot_area.layout().insertWidget(
            0, AdjustablePadding(self, self.top_view_export_plot)
        )

    def _hook_signals(self):
        self.update_side_view_preview.clicked.connect(
            self._on_update_sideview_preview_clicked
        )
        self.update_top_view_preview.clicked.connect(
            self._on_update_topview_preview_clicked
        )

        self.export_plots.clicked.connect(self._on_export_plots_clicked)
        self.cancel_export.clicked.connect(self.reject)

    @pyqtSlot()
    def _on_update_sideview_preview_clicked(self):
        """Update the sideview preview plot."""
        self.side_view_export_plot.modifiers = self.get_sideview_plot_modifiers()
        self.side_view_export_plot.title = self.side_view_plot_title.text()
        self.side_view_export_plot.point_types = self.get_sideview_point_types()
        self.side_view_export_plot.replot()

    @pyqtSlot()
    def _on_update_topview_preview_clicked(self):
        """Update the topview preview plot."""
        self.top_view_export_plot.title = self.top_view_plot_title.text()
        self.top_view_export_plot.numbers = self.top_view_numbers.isChecked()
        self.top_view_export_plot.rotation = self.top_view_rotation.value()
        self.top_view_export_plot.refresh()

    @pyqtSlot()
    def _on_export_plots_clicked(self):
        """Export the plots."""
        side_view_export = [False, "Side View"]
        top_view_export = [False, "Top View"]

        for export in (side_view_export, top_view_export):
            while not export[0]:
                export[0] = QFileDialog.getSaveFileName(
                    self.runner.window,
                    f"{export[1]} Export Location",
                    "",
                    f"Image or Vector (*.jpg, *.png, *.svg)",
                )[0]
                if export[0]:
                    break

        self.side_view_export_plot.export(side_view_export[0])
        self.top_view_export_plot.export(top_view_export[0])
