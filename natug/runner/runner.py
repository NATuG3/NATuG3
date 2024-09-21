import atexit
import logging
import os
import sys
from pathlib import Path

import PyQt6.uic
import pyqtgraph as pg
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QFileDialog

from natug import settings, ui

logger = logging.getLogger(__name__)


# All of the PyQt .ui files are stored in the natug directory, and load in at
# run time relative to the current working directory. However, the current
# working directory can change depending on how the program is run. To ensure
# that the .ui files are always loaded in correctly, we need to set the path to
# the natug directory as the path that this file exists at, up a level.

# To do this we simply monkey patch loadUi so that all of the calls to loadUi
# are relative to the correct path.

natug_path = (
    Path(__file__)
    .resolve()
    .parents[[p.name for p in Path(__file__).parents].index("natug")]
)

original_loadUi = PyQt6.uic.loadUi


def loadUi(*args, **kwargs):
    if (pyqt_loadui_root := os.getenv("PYQT_LOADUI_ROOT")) is not None:
        return original_loadUi(*(Path(pyqt_loadui_root) / args[0],), **kwargs)
    return original_loadUi(
        *(
            natug_path / args[0],
            *args[1:],
        ),
        **kwargs,
    )


PyQt6.uic.loadUi = loadUi


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
        booted (bool): Whether the program has been booted.

    Methods:
        recompute: Recompute the top and side view, and then refresh the plots.
    """

    restored_filepath = f"saves/restored.{settings.extension}"

    def __init__(self):
        from natug.runner.application import Application

        self.application = Application(self)
        self.window = None
        self.managers = None
        self.filehandler = None
        self.booted = False

        atexit.register(self.exit)

    @staticmethod
    def root() -> Path:
        return natug_path

    def exit(self):
        """
        Dump the program state at exit.
        """
        self.save(Runner.restored_filepath)
        logger.info("Dumped program state to %s", Runner.restored_filepath)

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
        4) Set up the application. This step sets up the application event loop,
            and connects the application to the main window.
        5) Set up the keyboard shortcuts. This step sets up the keyboard shortcuts
            for the application.
        """
        # set up pyqtgraph
        pg.setConfigOptions(
            useOpenGL=True, antialias=False, background=pg.mkColor(255, 255, 255)
        )

        # Create an instance of a filehandler, for saving/loading on the fly.
        from natug.runner.filehandler import FileHandler

        self.filehandler = FileHandler(self)
        logger.debug("Filehandler created")

        # Load in all the managers
        from natug.runner.managers import Managers

        self.managers = Managers(self)
        logger.debug("Managers created.")

        # Call the setup methods of the various managers. The order in which managers
        # are set up is very important, since some rely on others being already set
        # up (for example, we can't load the strands manager until the nucleic acid
        # profile manager has been loaded).
        self.managers.snapshots.setup()
        logger.debug("Managers loaded.")

        # Create a Window instance but don't set it up yet
        self.window = ui.Window(self)
        logger.debug("Main window created.")

        # Load the most recent program state
        try:
            if not os.path.isfile(Runner.restored_filepath):
                raise FileNotFoundError
            # Fill the current manager with dummy instances since the Window requires
            # SOME instance of SOME sort in order to load (even if it's an empty list of
            # domains).
            self.managers.fill_with_dummies()
            self.window.setup()
            self.load(Runner.restored_filepath, clear_nucleic_acid_profiles=False)
            logger.info("Restored program state from %s", Runner.restored_filepath)
        except (KeyError, FileNotFoundError):
            logger.warning("No program state to restore.")

            self.managers.nucleic_acid_profile.restore()
            self.managers.double_helices.restore()
            self.managers.strands.recompute()
            logger.debug("Restored default program state.")

            self.window.setup()
            logger.debug("Main window set up.")

        # We couldn't load the toolbar when we loaded the other managers because the
        # toolbar requires the main window to be created first.
        self.managers.toolbar.setup()
        logger.debug("Main window created.")

        # Set up the application
        self.application.setup()
        logger.debug("Application set up.")

        # Set up the keyboard shortcuts
        self._setup_shortcuts()
        logger.debug("Keyboard shortcuts set up.")

        # Resize the plots
        self.window.side_view.plot.auto_range()
        self.window.top_view.plot.auto_range()
        logger.debug("Plots resized.")

        # Set the booted flag to True
        self.booted = True

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
        if filepath and self.filehandler:
            self.filehandler.save(filepath)
            return True
        else:
            return False

    def load(self, filepath: str | None = None, *args, **kwargs):
        """
        Load a program state from a .natug file.

        Args:
            filepath (str): The path to the file to load. If None, a file dialog
                will be opened to select the file to load.
            *args, **kwargs: Arguments to be funneled to the file loader.

        Returns:
            False: If the user cancelled the file dialog.
            True: If the file was successfully loaded.

        Notes:
            This will overwrite the current program state.
        """
        if not filepath:
            filepath = QFileDialog.getOpenFileName(
                self.window,
                "Load Program State",
                "",
                f"NATuG Package (*.{settings.extension})",
            )[0]
        if filepath:
            self.filehandler.load(filepath, *args, **kwargs)
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

    def snapshot(self):
        """
        Take a snapshot of the current state of the program.
        """
        if self.booted:
            self.managers.snapshots.current.take_snapshot()

    def _setup_shortcuts(self):
        action = QAction(self.window)
        action.setShortcut(QKeySequence("Ctrl+Z"))
        action.triggered.connect(self.managers.snapshots.current.switch_to_previous)
        self.window.addAction(action)

        action = QAction(self.window)
        action.setShortcut(QKeySequence("Ctrl+Shift+Z"))
        action.triggered.connect(self.managers.snapshots.current.switch_to_next)
        self.window.addAction(action)

    def recompute(self):
        """Script to recompute top and side view data, and reload the plots."""
        self.window.config.panel.domains.dump_domains(self.managers.domains.current)
        self.managers.strands.recompute()
        self.window.top_view.refresh()
        self.window.side_view.refresh()
