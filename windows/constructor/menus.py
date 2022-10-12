from types import SimpleNamespace
from PyQt6.QtWidgets import QMenu

import helpers
from resources import fetch_icon
import webbrowser
from PyQt6.QtGui import QKeySequence
import references
import saves


parent = references.constructor.menu_bar


class File(QMenu):
    def __init__(self):
        super().__init__("&File", parent)

        # container for actions
        self.actions = SimpleNamespace()

        # file -> open
        open_ = self.actions.open = self.addAction("Open")
        open_.setIcon(fetch_icon("open-outline"))
        open_.setShortcut("ctrl+o")
        open_.setStatusTip("Open saved stage from file")
        open_.triggered.connect(lambda: saves.load.runner(parent))

        # file -> save
        save = self.actions.save = self.addAction("Save")
        save.setIcon(fetch_icon("save-outline"))
        save.setShortcut("ctrl+s")
        save.setStatusTip("Save current stage top file")
        save.triggered.connect(lambda: saves.save.runner(parent))

        # file -> save as
        save_as = self.actions.save_as = self.addAction("Save As")
        save_as.setIcon(fetch_icon("save-outline"))
        save_as.setShortcut(QKeySequence("ctrl+shift+s"))
        save_as.setStatusTip("Save current stage as new file")


class view(QMenu):
    def __init__(self):
        super().__init__("&View", parent)

        # container for actions
        self.actions = SimpleNamespace()

        # view -> "Config" -> hide/unhide
        configuration = self.actions.configuration = self.addAction("Config")
        configuration.setStatusTip("Display the configuration tab menu")
        # will be checked/unchecked based on if widget is shown
        configuration.setIcon(fetch_icon("eye-outline"))
        configuration.triggered.connect(
            lambda: helpers.reverse_hidenness(
                references.constructor.docked_widgets.configuration
            )
        )

        # view -> "top view" -> hide/unhide
        top_view = self.actions.top_view = self.addAction("Helicies Top View")
        top_view.setStatusTip("Display the helices top view graph")
        # will be checked/unchecked based on if widget is shown
        top_view.setIcon(fetch_icon("eye-outline"))
        top_view.triggered.connect(
            lambda: helpers.reverse_hidenness(
                references.constructor.docked_widgets.top_view
            )
        )


class help(QMenu):
    def __init__(self):
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
