import webbrowser
from types import SimpleNamespace

from PyQt6.QtWidgets import QMenu

from ui.resources import fetch_icon


class Help(QMenu):
    def __init__(self, parent):
        super().__init__("&Help", parent)

        # container for actions
        self.actions = SimpleNamespace()

        # help -> manual -> open manual pdf
        manual = self.actions.manual = self.addAction("Manual")
        manual.setIcon(fetch_icon("book-outline"))
        manual.setShortcut("ctrl+h")

        # help -> github -> open github project link
        github = self.actions.github = self.addAction("Github")
        github.setIcon(fetch_icon("logo-github"))
        github.triggered.connect(
            lambda: webbrowser.open_new_tab(
                "https://github.com/404Wolf/dna_nanotube_tools"
            )
        )

        # help -> about -> open about statement
        about = self.actions.about = self.addAction("About")
        about.setIcon(fetch_icon("information-outline"))
