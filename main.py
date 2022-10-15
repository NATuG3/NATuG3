def main():
    import logging

    # set log level
    logging.basicConfig(
        level=logging.DEBUG,
    )

    import config
    import storage
    from time import time
    import sys

    # mute pyqt logs
    logging.getLogger("PyQt6").setLevel(logging.INFO)

    # log boot statement
    logging.debug(f"Booting @ {time()}")

    if sys.platform.startswith("win"):
        # to get icon to work properly on Windows this code must be run
        # consult the below stackoverflow link for information on why
        # https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(__name__)

    # show the constructor window
    storage.windows.constructor.show()
    storage.windows.constructor.resizeEvent(None)  # trigger initial resize event
    logging.debug("Set up main window")

    # begin app event loop
    logging.debug("Beginning event loop...")
    sys.exit(storage.application.exec())


if __name__ == "__main__":
    main()
