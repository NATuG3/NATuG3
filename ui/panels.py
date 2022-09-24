from types import SimpleNamespace
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QTabWidget, QPushButton, QSpacerItem, QSizePolicy
from PyQt6 import uic


class title_panel(QWidget):
    def __init__(self):
        super().__init__()

        self.setLayout(QVBoxLayout())

        # add title widget
        title = QLabel("""<h1>DNA Nanotube Constructor</h1>""")
        self.layout().addWidget(title)


class config(QWidget):
    """A tab box for config and domain configuration"""

    def __init__(self) -> None:
        super().__init__()

        class tab_area(QTabWidget):
            """Settings/Domain tab area"""

            def __init__(subself):
                super().__init__()

                # container to store all tabs in
                subself.tabs = SimpleNamespace()

                class settings(QWidget):
                    def __init__(subsubself):
                        super().__init__()
                        uic.loadUi("ui/settings.ui", subsubself)

                subself.tabs.settings = settings()
                subself.tabs.domains = QLabel("Placeholder for domain tab")

                subself.addTab(subself.tabs.settings, "Settings")
                subself.addTab(subself.tabs.domains, "Domains")

        class preset_manager(QWidget):
            """Manager for config presets"""

            def __init__(subself):
                super().__init__()
                uic.loadUi("ui/preset_manager.ui", subself)

        class update_graphs(QPushButton):
            def __init__(self):
                super().__init__("Update Graphs")

        self.setLayout(QVBoxLayout())
        self.layout().addWidget(preset_manager())
        self.layout().addWidget(tab_area())
        self.layout().addItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.layout().addWidget(update_graphs())
