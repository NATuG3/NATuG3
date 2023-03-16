from dataclasses import dataclass
from typing import Tuple

from PyQt6 import uic
from PyQt6.QtWidgets import QDialog


@dataclass(slots=True, frozen=True)
class PlotExportData:
    x_range: Tuple[float, float]
    z_range: Tuple[float, float]
    top_view_filename: str
    side_view_filename: str
    filetype: str

class PlotExporter(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi("ui/dialogs/plot_exporter/plot_exporter.ui", self)
