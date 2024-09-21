from PyQt6.QtWidgets import QMenuBar


class Menubar(QMenuBar):
    """
    The file menu bar.

    This is the file menu bar that is displayed at the top of the window.

    Sections contained in the file menu bar include:
        - File
            - Open
            - Save
        - View
            - Config
            - Top View
            - Recolor Strands
        - Help
            - Manual
            - Github
            - About
    """

    def __init__(self, parent, runner: "runner.Runner"):
        """
        Initialize the file menu bar.

        Args:
            parent: The strands of the file menu bar.
        """
        self.runner = runner
        super().__init__(parent)
        self._add_menus()

    def _add_menus(self):
        """Add the menus to the menu bar."""
        from natug.ui.menubar import File, Help, View

        # add menus
        self.addMenu(File(self, self.runner))
        self.addMenu(View(self, self.runner))
        self.addMenu(Help(self))
