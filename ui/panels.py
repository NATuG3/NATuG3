from types import SimpleNamespace
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QTabWidget
from PyQt6 import uic


class title_panel(QWidget):
    def __init__(self):
        # this is an inherented class of QWidget
        # so we must initialize the parent qt widget
        super().__init__()

        self.setLayout(QVBoxLayout())

        # add title widget
        title = QLabel("""<h1>DNA Nanotube Constructor</h1>""")
        self.layout().addWidget(title)


class config(QTabWidget):
    """A tab box for config and domain configuration"""
    def __init__(self) -> None:
        # this is an inherented class of QWidget
        # so we must initialize the parent qt widget
        super().__init__()

        # container to store all tabs in
        self.tabs = SimpleNamespace()

        class settings(QWidget):
            def __init__(self):
                super().__init__()
                uic.loadUi("ui/settings.ui", self)

        self.tabs.settings = settings()
        self.tabs.domains = QLabel("Placeholder for domain tab")

        self.addTab(self.tabs.settings, "Settings")
        self.addTab(self.tabs.domains, "Domains")
