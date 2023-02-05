from PyQt6.QtWidgets import QMenu

from ui.resources import fetch_icon


class File(QMenu):
    """
    The file section of the menu bar.

    This is a submenu of the menu bar that contains the following actions:
        - Open
        - Save
    """

    def __init__(self, parent):
        """
        Initialize the file section of the menu bar.

        Args:
            parent: The strands of the file section of the menu bar.
        """
        super().__init__("&File", parent)

    def _open(self):
        """Open a save of a state of the program. This loads strands, domains,
        and nucleic acid settings."""
        open_ = self.actions.open = self.addAction("Open")
        open_.setIcon(fetch_icon("open-outline"))
        open_.setShortcut("ctrl+o")
        open_.setStatusTip("Open saved stage from file")
        open_.triggered.connect(lambda: runner.saver.load.runner(self.parent()))

    def _save(self):
        """Save the current state of the program. This saves strands, domains,
        and nucleic acid settings."""
        save = self.actions.save = self.addAction("Save")
        save.setIcon(fetch_icon("save-outline"))
        save.setShortcut("ctrl+s")
        save.setStatusTip("Save current stage top file")
        save.triggered.connect(lambda: runner.saver.save.runner(self.parent()))
