from dataclasses import dataclass
from PyQt6.QtWidgets import QMainWindow, QDialog


@dataclass
class windows:
    """Dataclass to store references to all windows in."""

    constructor: QMainWindow = None
    sequencer: QMainWindow = None
    saver: QDialog = None


windows = windows()
