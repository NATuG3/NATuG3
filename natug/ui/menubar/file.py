from PyQt6.QtWidgets import QMenu

from natug.ui.resources import fetch_icon


class File(QMenu):
    """
    The file section of the menu bar.

    This is a submenu of the menu bar that contains the following actions:
        - Open
        - Save
    """

    def __init__(self, parent, runner):
        """
        Initialize the file section of the menu bar.

        Args:
            parent: The strands of the file section of the menu bar.
        """
        self.runner = runner
        super().__init__("&File", parent)

        self._open()
        self._save()

    def _open(self):
        """Open a save of a state of the program. This loads strands, domains,
        and nucleic acid settings."""
        self.open = self.addAction("Open")
        self.open.setIcon(fetch_icon("open-outline"))
        self.open.setShortcut("ctrl+o")
        self.open.setStatusTip("Open saved stage from file")
        self.open.triggered.connect(self.runner.load)

    def _save(self):
        """Save the current state of the program. This saves strands, domains,
        and nucleic acid settings."""
        self.save = self.addAction("Save")
        self.save.setIcon(fetch_icon("save-outline"))
        self.save.setShortcut("ctrl+s")
        self.save.setStatusTip("Save current stage top file")
        self.save.triggered.connect(self.runner.save)
