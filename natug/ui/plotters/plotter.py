import logging
from os.path import abspath

import pyqtgraph as pg
import pyqtgraph.exporters

from natug.utils import show_in_file_explorer

logger = logging.getLogger(__name__)


class Plotter(pg.PlotWidget):
    def export(
        self,
        filepath: str,
        show_after_export: bool = True,
    ):
        """
        Export the plot to image file.

        Args:
            filepath: The path to save the image to. Include the file extension.
                Options are .svg, .png, and .jpg.
            show_after_export: Whether to show the file in the file explorer after
                exporting. Defaults to True.
        """
        # Create the exporter
        if filepath.endswith(".svg"):
            exporter = pg.exporters.SVGExporter(self.scene())
        else:
            exporter = pg.exporters.ImageExporter(self.scene())

        # Export the image
        exporter.export(filepath)

        # Show the file in the file explorer
        if show_after_export:
            show_in_file_explorer(abspath(filepath))

        logger.info(f"Exported plot to %s.", filepath)
