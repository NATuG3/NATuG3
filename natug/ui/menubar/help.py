import webbrowser

from PyQt6.QtWidgets import QMenu

from natug import settings
from natug.ui.resources import fetch_icon


class Help(QMenu):
    """
    The help section of the menu bar.

    This is a submenu of the menu bar that contains the following actions:
        - Manual: Open the manual pdf.
        - Github: Open the github project link.
        - About: Obtain information about NATuG.
    """

    def __init__(self, parent):
        """
        Initialize the help section of the menu bar.

        Args:
            parent: The strands of the help section of the menu bar.
        """
        super().__init__("&Help", parent)

        self._about()
        self._manual()
        self._github()

    def _manual(self):
        """Open NATuG's manual."""
        self.manual = self.addAction("Manual")
        self.manual.setIcon(fetch_icon("book-outline"))
        self.manual.setShortcut("ctrl+h")

    def _github(self):
        """Open the project's GitHub page."""
        self.github = self.addAction("Github")
        self.github.setIcon(fetch_icon("logo-github"))
        self.github.triggered.connect(lambda: webbrowser.open_new_tab(settings.github))

    def _about(self):
        """Get information about NATuG."""
        self.about = self.addAction("About")
        self.about.setIcon(fetch_icon("information-outline"))
