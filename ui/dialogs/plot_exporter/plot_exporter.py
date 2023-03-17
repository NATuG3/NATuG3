from dataclasses import dataclass
from typing import Tuple

from PyQt6 import uic
from PyQt6.QtWidgets import QDialog


@dataclass(slots=True, frozen=True, kw_only=True)
class PlotExportData:
    """
    The data needed to export the top and side view plots.

    Attributes:
        x_range: The x range that the user wants to export.
        z_range: The z range that the user wants to export.
        top_view_filename: The filename of the top view plot image export.
        side_view_filename: The filename of the side view plot image export.
        filetype: The filetype of the image export. Must be "PNG," "JPG," or "SVG."
    """

    x_range: Tuple[float, float] = (0, 0)
    z_range: Tuple[float, float] = (0, 0)
    height: float = 450
    width: float = 900
    top_view_filename: str = "top-view"
    side_view_filename: str = "side-view"
    filetype: str = "SVG"


class PlotExporter(QDialog):
    """
    The plot exporter dialog.

    This dialog allows the user to export the top and side view plots as high resolution
    images (PNG or JPG) or vector graphics (SVG).
    """

    def __init__(self, parent, x_range, z_range):
        """
        Initialize the plot exporter dialog.

        Args:
            x_range: The x range of the entire plot.
            z_range: The z range of the entire plot.
        """
        super().__init__(parent)
        uic.loadUi("ui/dialogs/plot_exporter/plot_exporter.ui", self)
        self.set_data(PlotExportData(x_range=x_range, z_range=z_range))
        self.cancel_export.clicked.connect(self.reject)
        self.export_plots.clicked.connect(self.accept)

    @classmethod
    def run(cls, parent, x_range, z_range):
        """
        Run the plot exporter dialog.

        Returns:
            The data entered by the user, or None if the user cancelled the dialog.
        """
        dialog = cls(parent, x_range, z_range)
        result = dialog.exec()
        if result == QDialog.DialogCode.Accepted:
            return dialog.fetch_data()
        else:
            return None

    def _prettify(self):
        """Prettify the dialog."""
        self.setFixedWidth(100)
        self.setFixedHeight(130)

    def fetch_data(self) -> PlotExportData:
        """Fetch the current data from the dialog."""
        return PlotExportData(
            x_range=(self.from_x.value(), self.to_x.value()),
            z_range=(self.from_z.value(), self.to_z.value()),
            top_view_filename=self.topview_filename.text(),
            side_view_filename=self.sideview_filename.text(),
            filetype=self.filetype_dropdown.currentText(),
            height=self.image_height.value(),
            width=self.image_width.value(),
        )

    def set_data(self, data: PlotExportData):
        """Set the current data of the dialog."""
        self.from_x.setValue(data.x_range[0])
        self.to_x.setValue(data.x_range[1])
        self.from_z.setValue(data.z_range[0])
        self.to_z.setValue(data.z_range[1])
        self.topview_filename.setText(data.top_view_filename)
        self.sideview_filename.setText(data.side_view_filename)
        self.filetype_dropdown.setCurrentText(data.filetype)
        self.image_height.setValue(data.height)
        self.image_width.setValue(data.width)
