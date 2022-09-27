from types import SimpleNamespace
from PyQt6.QtWidgets import QMenu
import ui.slots
import webbrowser
from PyQt6.QtGui import QKeySequence

# the parent for all menus
import database.ui
parent_menu = database.ui.window.menu_bar

class file(QMenu):
    def __init__(self):
        super().__init__("&File", parent_menu)

        self.actions = SimpleNamespace()

        # file -> open
        open = self.actions.open = self.addAction("Open")
        open.setShortcuts((QKeySequence("control+o"), QKeySequence("command+o")))
        open.setStatusTip("Open saved stage from file")

        # file -> save
        save = self.actions.save = self.addAction("Save")
        save.setShortcuts((QKeySequence("control+s"), QKeySequence("command+s")))
        save.setStatusTip("Save current stage top file")

        # file -> save as
        save_as = self.actions.save_as = self.addAction("Save As")
        save_as.setShortcuts((QKeySequence("control+shift+s"), QKeySequence("command+shift+s")))
        save_as.setStatusTip("Save current stage as new file")

class view(QMenu):
    def __init__(self):
        super().__init__("&View", parent_menu)

        self.actions = SimpleNamespace()

        # view -> "settings" -> hide/unhide
        config = self.actions.config = self.addAction("Config")
        config.setStatusTip("Display the config tab menu")
        config.setChecked(True)
        config.setCheckable(True)
        config.toggled.connect(
            lambda: ui.slots.hide_or_unhide(self.docked_widgets.config)
        )

        # view -> "top view" -> hide/unhide
        top_view = self.actions.top_view = self.addAction("Helicies Top View")
        top_view.setStatusTip(
            "Display the helicies top view graph"
        )
        top_view.setChecked(True)
        top_view.setCheckable(True)
        top_view.toggled.connect(
            lambda: ui.slots.hide_or_unhide(self.docked_widgets.top_view)
        )

class help(QMenu):
    def __init__(self):
        super().__init__("&Help", parent_menu)

        # help -> manual -> open manual pdf
        self.actions = SimpleNamespace()
        manual = self.actions.manual = self.addAction("Manual")
        manual.setShortcuts((QKeySequence("control+h"), QKeySequence("command+h")))

        # help -> github -> open github project link
        github = self.actions.github = self.addAction("Github")
        github.triggered.connect(
            lambda: webbrowser.open_new_tab(
                "https://github.com/404Wolf/dna_nanotube_tools"
            )
        )

        # help -> about -> open about statement
        about = self.actions.about = self.addAction("About")