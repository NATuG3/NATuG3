import webbrowser
from types import SimpleNamespace

from PyQt6.QtWidgets import QMenu

import settings
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
        github.triggered.connect(lambda: webbrowser.open_new_tab(settings.github))

        # help -> about -> open about statement
        about = self.actions.about = self.addAction("About")
        about.setIcon(fetch_icon("information-outline"))
