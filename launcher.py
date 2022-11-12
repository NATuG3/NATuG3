import logging
from time import time

# whether to delete restoration files
RESET = False

# refs script logger object
logger = logging.getLogger(__name__)

# mute pyqt logs
logging.getLogger("PyQt6").setLevel(logging.INFO)


def main():
    """Main runner for program."""

    if RESET:
        from os import remove
        from contextlib import suppress

        with suppress(FileNotFoundError):
            remove("saves/nucleic_acid/profiles.nano")
            remove("saves/nucleic_acid/restored.nano")
            remove("saves/domains/restored.nano")
            remove("saves/strands/restored.nano")

    import pyqtgraph as pg

    pg.setConfigOptions(
        useOpenGL=True, antialias=False, background=pg.mkColor(255, 255, 255)
    )

    import refs

    # set log level
    logging.basicConfig(
        level=logging.DEBUG,
    )

    logger.debug(f"Booting @ {time()}")

    logger.info("Loaded profiles and domain settings.")

    import sys

    if sys.platform.startswith("win"):
        # to get icon to work properly on Windows this code must be run
        # consult the below stackoverflow link for information on why
        # https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(__name__)

    logger.info("Loaded the config.")

    # show the ui window
    refs.constructor.show()
    refs.constructor.resizeEvent(None)  # trigger initial resize event
    logger.debug("Set up refs window")

    # begin app event loop
    logger.debug("Beginning event loop...")
    sys.exit(refs.application.exec())


if __name__ == "__main__":
    main()
