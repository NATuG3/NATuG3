from dataclasses import dataclass
from types import SimpleNamespace
from PyQt6.QtWidgets import QMainWindow, QWidget

"""Note that this file enables cross-module access to UI widgets"""

# will be set by main app
window: QMainWindow


@dataclass
class widgets:
    """Storage space for all widgets"""

    top_view: QWidget = None
    side_view: QWidget = None


widgets = SimpleNamespace()
