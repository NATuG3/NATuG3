from types import SimpleNamespace
from PyQt6.QtWidgets import QMenu
from resources import fetch_icon
import webbrowser
from PyQt6.QtGui import QKeySequence, QShortcut
import references

parent = references.constructor.menu_bar


class File(QMenu):
    def __init__(self):
        super().__init__("&File", parent)

        # container for actions
        self.actions = SimpleNamespace()

        # file -> open
        open = self.actions.open = self.addAction("Open")
        open.setIcon(fetch_icon("open-outline"))
        open.setShortcut("ctrl+o")
        open.setStatusTip("Open saved stage from file")

        # file -> save
        save = self.actions.save = self.addAction("Save")
        save.setIcon(fetch_icon("save-outline"))
        save.setShortcut("ctrl+s")
        save.setStatusTip("Save current stage top file")

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

        def hide_or_unhide(potentially_hidden_item, menu_item):
            """Reverse the hiddenness of a widget"""
            if potentially_hidden_item.isHidden():
                potentially_hidden_item.show()
                menu_item.setIcon(fetch_icon("eye-off-outline"))
            else:
                potentially_hidden_item.hide()
                menu_item.setIcon(fetch_icon("eye-outline"))

        # view -> "Config" -> hide/unhide
        config = self.actions.config = self.addAction("Config")
        config.setStatusTip("Display the config tab menu")
        # will be checked/unchecked based on if widget is shown
        config.setIcon(fetch_icon("eye-off-outline"))
        config.triggered.connect(
            lambda: hide_or_unhide(
                references.Windows.constructor.docked_widgets.config, config
            )
        )

        # view -> "top view" -> hide/unhide
        top_view = self.actions.top_view = self.addAction("Helicies Top View")
        top_view.setStatusTip("Display the helicies top view graph")
        # will be checked/unchecked based on if widget is shown
        top_view.setIcon(fetch_icon("eye-off-outline"))
        top_view.triggered.connect(
            lambda: hide_or_unhide(
                references.Windows.constructor.docked_widgets.top_view, top_view
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
