import sys

from PyQt6.QtWidgets import QApplication

from structures.points import NEMid
from structures.profiles import NucleicAcidProfile
from structures.strands import Strand
from ui.dialogs.strand_config.strand_config import StrandConfig


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    nucleic_acid_profile = NucleicAcidProfile()
    NEMids = [NEMid(1, 2), NEMid(2, 3), NEMid(3, 4)]
    strand = Strand(nucleic_acid_profile)
    strand.sequence = list("ATATATAGGGGCCCC")

    widget = StrandConfig(None, strand)
    widget.show()

    app.exec()
    sys.exit(app)


if __name__ == "__main__":
    main()
