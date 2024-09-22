import logging
import os
import shutil
import sys
from contextlib import suppress
from pathlib import Path
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


def copy_files(src, dst):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            os.makedirs(d, exist_ok=True)
            copy_files(s, d)
        else:
            shutil.copyfile(s, d)


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

    if not os.path.exists("saves"):
        # Copy over the saves folder from __file__/saves to ./saves
        copy_files(Path(__file__).parent / "saves", "saves")
        os.mkdir(Path.cwd() / "saves/snapshots")
    else:
        for directory in (
            f"saves/domains",
            f"saves/strands",
            f"saves/nucleic_acid",
            f"saves/snapshots",
        ):
            with suppress(FileExistsError):
                os.mkdir(Path.cwd() / directory)

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
