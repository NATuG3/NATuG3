import logging

from PyQt6.QtWidgets import QDialog
from PyQt6 import uic

from natug.constants.directions import *
from natug.structures.domains import Domains
from natug.structures.points import Nucleoside
from natug.structures.strands import Strands

logger = logging.getLogger(__name__)


class NucleosideInformer(QDialog):
    """A QDialog to display information about a Nucleoside."""

    def __init__(
        self, parent, nucleoside: Nucleoside, all_strands: Strands, all_domains: Domains
    ):
        """
        Initialize the NucleosideInformer.

        Args:
            parent: The strands widget for the dialog.
            nucleoside: The Nucleoside to display information about.
            all_strands: The strands that contain the Nucleoside.
            all_domains: The domains that contain the Nucleoside.
        """
        super().__init__(parent)
        assert isinstance(all_strands, Strands)
        assert isinstance(all_domains, Domains)
        assert isinstance(nucleoside, Nucleoside)

        self.setWindowTitle("Nucleoside Information")
        uic.loadUi("./ui/dialogs/informers/nucleoside.ui", self)

        logger.info("Displaying information for %s", nucleoside)

        self.x_coordinate.setText(f"{nucleoside.x_coord:.4f} nanometers")
        self.z_coordinate.setText(f"{nucleoside.z_coord:.4f} nanometers")
        self.angle.setText(f"{nucleoside.angle:.4f}°")

        strand_index = all_strands.index(nucleoside.strand)
        if nucleoside.strand.closed:
            openness = "closed"
        else:  # not item.strand.closed
            openness = "open"
        self.strand.setText(
            f"nucleoside #"
            f"{nucleoside.strand.items.by_type(Nucleoside).index(nucleoside) + 1} in"
            f" {openness} strand #{strand_index + 1}"
        )
        self.helix.setText(
            f"nucleoside {nucleoside.helical_index} of helix {id(nucleoside.helix)}"
        )

        self.original_domain.setText(
            f"domain #{nucleoside.domain.index + 1} of {all_domains.count} domains"
        )

        if nucleoside.direction == UP:
            self.up.setChecked(True)
        elif nucleoside.direction == DOWN:
            self.down.setChecked(True)

        style = (
            "QTextEdit{{"
            "color: rgb(0, 0, 0); "
            "font-size: {font_size}px; "
            "text-align: center; "
            "background: rgb(255, 255, 255)"
            "}};"
        )
        if nucleoside.base is None:
            self.base.setStyleSheet(style.format(font_size=10))
            self.base.setText("Unset\nBase")
        else:
            self.base.setStyleSheet(style.format(font_size=32))
            self.base.setText(nucleoside.base)
