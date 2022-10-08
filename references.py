from dataclasses import dataclass
from PyQt6.QtWidgets import QMainWindow, QDialog, QApplication

app: QApplication = None

@dataclass
class windows:
    """Dataclass to store references to all windows in."""

    constructor: QMainWindow = None
    sequencer: QMainWindow = None
    saver: QDialog = None


windows = windows()


