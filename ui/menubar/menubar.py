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
    def __init__(self, parent):
        """
        Initialize the file menu bar.

        Args:
            parent: The parent of the file menu bar.
        """
        super().__init__(parent)
        self._add_menus()

    def _add_menus(self):
        """Add the menus to the menu bar."""
        from ui.menubar import File, View, Help
        # add menus
        self.addMenu(File(self))
        self.addMenu(View(self))
        self.addMenu(Help(self))
