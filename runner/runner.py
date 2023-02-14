import logging
import sys

import pyqtgraph as pg
from PyQt6.QtWidgets import QFileDialog

import settings
import ui
from structures.nanostructures.nanostructure import Nanostructure

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

    def nanostructure(self):
        """
        Obtain the current nanostructure.

        A Nanostructure object is created from the current strands, domains, and
        nucleic acid profile, all combined into a single object.

        Returns:
            Nanostructure: The current nanostructure.
        """

        return Nanostructure(
            strands=self.managers.strands.current,
            nucleic_acid_profile=self.managers.nucleic_acid_profile.current,
            domains=self.managers.domains.current,
        )

    def save(self):
        """
        Initiate the save process, allowing the user to save the current nanostructure.
        """
        filepath = QFileDialog.getSaveFileName(
            self.window,
            "Save Program State",
            "",
            f"NATuG Package (*.{settings.package_extension})",
        )[0]
        if filepath:
            self.filehandler.save(filepath)

    def load(self):
        """
        Initiate the load proxcess, allowing the user to load a nanostructure.
        """
        filepath = QFileDialog.getOpenFileName(
            self.window,
            "Load Program State",
            "",
            f"NATuG Package (*.{settings.package_extension})",
        )[0]
        if filepath:
            self.filehandler.load(filepath)

    def boot(self):
        """
        Run the program and show the main window.

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
