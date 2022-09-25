from types import SimpleNamespace
from PyQt6.QtWidgets import QMenu
import webbrowser
import ui.helpers


class view(QMenu):
    """View Menu."""

    def __init__(self, main_window):
        super().__init__("&View")

        # container to store actions in
        self.actions = SimpleNamespace()

        # view -> "Config" -> hide/unhide
        self.actions.config = self.addAction("Config")
        self.actions.config.setStatusTip("Display the config tab menu")
        self.actions.config.setChecked(True)  # by default config is shown
        self.actions.config.setCheckable(True)  # top view can be hidden
        # when clicked reverse hidden state of the config panel
        self.actions.config.toggled.connect(
            lambda: ui.helpers.hide_or_unhide(main_window.docked_items.config)
        )

        # view -> "top view" -> hide/unhide
        self.actions.top_view = self.addAction("Helicies Top View")
        self.actions.config.setStatusTip("Display the helicies top view graph")
        self.actions.top_view.setChecked(True)  # by default top_view is shown
        self.actions.top_view.setCheckable(True)  # top view can be hidden
        # when clicked reverse hidden state of the top view graph
        self.actions.top_view.toggled.connect(
            lambda: ui.helpers.hide_or_unhide(main_window.docked_items.top_view)
        )


class help(QMenu):
    """Help Menu."""

    def __init__(self):
        super().__init__("&Help")

        # container to store actions in
        self.actions = SimpleNamespace()

        # help -> manual -> open manual pdf
        self.actions.manual = self.addAction("Manual")

        # help -> github -> open github project link
        self.actions.github = self.addAction("Github")
        self.actions.github.triggered.connect(
            lambda: webbrowser.open_new_tab(
                "https://github.com/404Wolf/dna_nanotube_tools"
            )
        )

        # help -> about -> open about statement
        self.actions.about = self.addAction("About")
