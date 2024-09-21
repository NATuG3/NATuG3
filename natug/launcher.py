import logging
import os
import sys
from contextlib import suppress
from time import time

from natug.runner import Runner
from natug.ui.splash_screen import SplashScreen

RESET = False

# refs script logger object
logger = logging.getLogger(__name__)

# mute pyqt logs
logging.getLogger("PyQt6").setLevel(logging.WARNING)

# create the main program runner
runner = Runner()


def launch():
    """Main runner for program."""

    # set up logging
    logging.basicConfig(
        level=logging.DEBUG,
    )

    if RESET:
        for filepath in (
            f"saves/domains/restored.csv",
            f"saves/strands/restored.csv",
        ):
            with suppress(FileNotFoundError):
                os.remove(filepath)

        for snapshot in os.listdir("saves/snapshots"):
            os.remove(f"saves/snapshots/{snapshot}")

    for directory in (
        f"saves/domains",
        f"saves/strands",
        f"saves/nucleic_acid",
        f"saves/snapshots",
    ):
        with suppress(FileExistsError):
            os.mkdir(directory)

    logger.debug(f"Booting @ %s", {time()})

    if sys.platform.startswith("win"):
        # to get icon to work properly on Windows this code must be run
        # consult the below stackoverflow link for information on why
        # https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(__name__)

    # create the splash screen
    splash_screen = SplashScreen()
    splash_screen.show()

    # set up the runner
    runner.setup()

    # close the splash screen and run the program
    splash_screen.finish(runner.window)

    # close the splash screen and run the program
    # splash_screen.finish(runner.window)
    runner.boot()


if __name__ == "__main__":
    launch()
