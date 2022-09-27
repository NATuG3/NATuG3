from types import SimpleNamespace
from PyQt6.QtWidgets import QMenu
import ui.helpers
import webbrowser
from PyQt6.QtGui import QKeySequence

# the parent for all menus
import database.ui

parent_menu = database.ui.windows.main.menu_bar


class file(QMenu):
    def __init__(self):
        super().__init__("&File", parent_menu)

        # container for actions
        self.actions = SimpleNamespace()

        # file -> open
        open = self.actions.open = self.addAction("Open")
        open.setIcon(ui.helpers.fetch_icon("open-outline"))
        open.setShortcut(QKeySequence("ctrl+o"))
        open.setStatusTip("Open saved stage from file")

        # file -> save
        save = self.actions.save = self.addAction("Save")
        save.setIcon(ui.helpers.fetch_icon("save-outline"))
        save.setShortcut(QKeySequence("ctrl+s"))
        save.setStatusTip("Save current stage top file")

        # file -> save as
        save_as = self.actions.save_as = self.addAction("Save As")
        save_as.setIcon(ui.helpers.fetch_icon("save-outline"))
        save_as.setShortcut(QKeySequence("ctrl+shift+s"))
        save_as.setStatusTip("Save current stage as new file")


class view(QMenu):
    def __init__(self):
        super().__init__("&View", parent_menu)

        # container for actions
        self.actions = SimpleNamespace()

        def hide_or_unhide(potentially_hidden_item, menu_item):
            """Reverse the hiddenness of a widget"""
            if potentially_hidden_item.isHidden():
                potentially_hidden_item.show()
                menu_item.setIcon(ui.helpers.fetch_icon("eye-off-outline"))
            else:
                potentially_hidden_item.hide()
                menu_item.setIcon(ui.helpers.fetch_icon("eye-outline"))
                
                
        # view -> "Config" -> hide/unhide
        config = self.actions.config = self.addAction("Config")
        config.setStatusTip("Display the config tab menu")
        # will be checked/unchecked based on if widget is shown
        config.setIcon(ui.helpers.fetch_icon("eye-off-outline"))
        config.triggered.connect(
            lambda: hide_or_unhide(database.ui.window.docked_widgets.config, config)
        )

        # view -> "top view" -> hide/unhide
        top_view = self.actions.top_view = self.addAction("Helicies Top View")
        top_view.setStatusTip("Display the helicies top view graph")
        # will be checked/unchecked based on if widget is shown
        top_view.setIcon(ui.helpers.fetch_icon("eye-off-outline"))
        top_view.triggered.connect(
            lambda: hide_or_unhide(database.ui.window.docked_widgets.top_view, top_view)
        )

        # view -> update graphs
        update_graphs = self.actions.update_graphs = self.addAction("Update Graphs")
        update_graphs.setIcon(ui.helpers.fetch_icon("refresh-outline"))
        update_graphs.setStatusTip(
            'Update the graphs (equivalent to pressing the "update graphs" button)'
        )
        update_graphs.setShortcut(QKeySequence("ctrl+u"))


class help(QMenu):
    def __init__(self):
        super().__init__("&Help", parent_menu)

        # container for actions
        self.actions = SimpleNamespace()

        # help -> manual -> open manual pdf
        manual = self.actions.manual = self.addAction("Manual")
        manual.setIcon(ui.helpers.fetch_icon("book-outline"))
        manual.setShortcuts((QKeySequence("control+h"), QKeySequence("command+h")))

        # help -> github -> open github project link
        github = self.actions.github = self.addAction("Github")
        github.setIcon(ui.helpers.fetch_icon("logo-github"))
        github.triggered.connect(
            lambda: webbrowser.open_new_tab(
                "https://github.com/404Wolf/dna_nanotube_tools"
            )
        )

        # help -> about -> open about statement
        about = self.actions.about = self.addAction("About")
        about.setIcon(ui.helpers.fetch_icon("information-outline"))
