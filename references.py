from dataclasses import dataclass
from PyQt6.QtWidgets import QMainWindow, QDialog, QWidget
from config.nucleic_acid import profile


@dataclass
class windows:
    """Dataclass to store references to all windows in."""

    constructor: QMainWindow = None
    sequencer: QMainWindow = None
    saver: QDialog = None


windows = windows()


@dataclass
class miscellaneous:
    """Dataclass to store all other needed references"""

    current_graphs_profile: profile = None


miscellaneous = miscellaneous()
