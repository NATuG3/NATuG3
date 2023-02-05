import logging
import os
import sys
from contextlib import suppress
from threading import Thread
from time import time, sleep

from runner import Runner
from ui.splash_screen import SplashScreen

RESET = True

# refs script logger object
logger = logging.getLogger(__name__)

# mute pyqt logs
logging.getLogger("PyQt6").setLevel(logging.WARNING)

# create the main program runner
runner = Runner()


def main():
    """Main runner for program."""

    # set up logging
    logging.basicConfig(
        level=logging.DEBUG,
    )

    if RESET:
        for filepath in (
            f"saves/domains/restored.nano",
            f"saves/strands/restored.nano",
        ):
            with suppress(FileNotFoundError):
                os.remove(filepath)

    # create needed files
    with suppress(FileExistsError):
        os.mkdir(f"{os.getcwd()}/saves/nucleic_acid")
        os.mkdir(f"{os.getcwd()}/saves/domains")
        os.mkdir(f"{os.getcwd()}/saves/strands")

    logger.debug(f"Booting @ {time()}")

    if sys.platform.startswith("win"):
        # to get icon to work properly on Windows this code must be run
        # consult the below stackoverflow link for information on why
        # https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(__name__)

    splash_screen = SplashScreen()
    splash_screen.show()

    # set up the runner
    runner.setup()

    splash_screen.finish(runner.window)

    # close the splash screen and run the program
    # splash_screen.finish(runner.window)
    runner.boot()


if __name__ == "__main__":
    main()
