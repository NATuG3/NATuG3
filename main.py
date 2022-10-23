import logging
from time import time

# main script logger
logger = logging.getLogger("main")

# mute pyqt logs
logging.getLogger("PyQt6").setLevel(logging.INFO)


def main():
    # set log level
    logging.basicConfig(
        level=logging.DEBUG,
    )

    logger.debug(f"Booting @ {time()}")

    import domains.storage
    import nucleic_acid.storage

    domains.storage.load()
    nucleic_acid.storage.load()

    logger.info("Loaded profiles and domain settings.")

    import runner
    import sys

    if sys.platform.startswith("win"):
        # to get icon to work properly on Windows this code must be run
        # consult the below stackoverflow link for information on why
        # https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(__name__)

    logger.info("Loaded the config.")

    # show the constructor window
    runner.windows.constructor.show()
    runner.windows.constructor.resizeEvent(None)  # trigger initial resize event
    logger.debug("Set up main window")

    # begin app event loop
    logger.debug("Beginning event loop...")
    sys.exit(runner.application.exec())


if __name__ == "__main__":
    main()
