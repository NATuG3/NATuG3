import logging
import sys

import pyqtgraph as pg
from PyQt6.QtWidgets import QFileDialog

import settings
import ui

logger = logging.getLogger(__name__)


class Runner:
    """
    The main runner for NATuG.

    This sets up and stores all the needed managers, and then runs the program.
    Various properties, such as Strands, Domains, and NucleicAcidProfiles will be
    stored under runner.

    Attributes:
        application (Application): The main QApplication instance.
        window (ui.Window): The main window of the application.
        managers (Managers): The managers for the application. The managers store
            all the various pieces of live data for the program, and are used to
            access and modify them. Additionally, they handle automated loading and
            saving upon exit/boot.
        filehandler (logging.FileHandler): The file handler for the logger. This
            is used to save and load the program state at the request of the user.
    """

    def __init__(self):
        from runner.application import Application

        self.application = Application()
        self.window = None
        self.managers = None
        self.filehandler = None

    def setup(self):
        """
        Set up all necessary prerequisites for running the program.

        1) Load in all the managers. The managers store all the various pieces of
            live data for the program, and are used to access and modify them.
            Additionally, they handle automated loading and saving upon exit/boot.
        2) Create the main QApplication. This step also sets up custom settings for
            the application, such as high DPI dynamic scaling.
        3) Create the main window. This is the main window of the application, and
            is the parent of all other windows.
        """
        # set up pyqtgraph
        pg.setConfigOptions(
            useOpenGL=True, antialias=False, background=pg.mkColor(255, 255, 255)
        )

        # Load in all the managers
        from runner.managers import Managers

        self.managers = Managers(self)

        # Call the setup methods of the various managers. The order in which managers
        # are set up is very important, since some rely on others being already set
        # up (for example, we can't load the strands manager until the nucleic acid
        # profile manager has been loaded).
        self.managers.nucleic_acid_profile.setup()
        self.managers.domains.setup()
        self.managers.double_helices.setup()
        self.managers.strands.setup()
        logger.debug("Managers loaded.")

        # Create an instance of a filehandler, for saving/loading on the fly.
        from runner.filehandler import FileHandler

        self.filehandler = FileHandler(self)

        # Create a main window instance
        self.window = ui.Window(self)
        self.window.setup()
        # We couldn't load the toolbar when we loaded the other managers because the
        # toolbar requires the main window to be created first.
        self.managers.toolbar.setup()
        logger.debug("Main window created.")

    def save(self, filepath: str | None = None):
        """
        Save the program state to a .natug file.

        Returns:
            False: If the user cancelled the file dialog.
            True: If the file was successfully saved.

        Args:
            filepath (str): The path to the file to save. If None, a file dialog
                will be opened to select the file to save.
        """
        if not filepath:
            filepath = QFileDialog.getSaveFileName(
                self.window,
                "Save Program State",
                "",
                f"NATuG Package (*.{settings.extension})",
            )[0]
        if filepath:
            self.filehandler.save(filepath)
            return True
        else:
            return False

    def load(self, filepath: str | None = None):
        """
        Load a program state from a .natug file.

        Args:
            filepath (str): The path to the file to load. If None, a file dialog
                will be opened to select the file to load.

        Returns:
            False: If the user cancelled the file dialog.
            True: If the file was successfully loaded.

        Notes:
            This will overwrite the current program state.
        """
        if filepath is None:
            filepath = QFileDialog.getOpenFileName(
                self.window,
                "Load Program State",
                "",
                f"NATuG Package (*.{settings.extension})",
            )[0]
        if filepath:
            self.filehandler.load(filepath)
            return True
        else:
            return False

    def boot(self):
        """
        Run the program and show the main window. This must be run after setup().

        1) Show the main window. This makes the main window visible.
        2) Trigger an initial resize event. This is necessary to ensure that the
            main window is properly sized on launch.
        3) Begin the application event loop.
        """
        self.window.show()

        self.window.resizeEvent(None)  # trigger initial resize event
        logger.debug("Main window shown.")

        # begin app event loop
        logger.debug("Beginning event loop...")
        sys.exit(self.application.exec())
