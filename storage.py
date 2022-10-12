from PyQt6.QtWidgets import QApplication
from types import SimpleNamespace

# QApplication
application: QApplication = None

# All windows of application
windows = SimpleNamespace(constructor=None, sequencer=None)

# DNA Plots
plots = SimpleNamespace(top_view=None, side_view=None)