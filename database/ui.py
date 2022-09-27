from dataclasses import dataclass
from types import SimpleNamespace
from PyQt6.QtWidgets import QMainWindow, QWidget

@dataclass
class windows:
    """Storage container for window instances"""
    main: QMainWindow = None
windows = SimpleNamespace()

@dataclass
class widgets:
    """Storage container for widget instances"""
    side_view: QWidget = None
    top_view: QWidget = None
widgets = widgets()