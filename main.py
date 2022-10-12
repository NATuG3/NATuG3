from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import sys
from time import time
import logging
import storage

DEBUG = True


def main():
    """Main program runner."""

    if sys.platform.startswith("win"):
        # to get icon to work properly on Windows this code must be run
        # consult the below stackoverflow link for information on why
        # https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(__name__)

    def logger():
        # initialize logging
        if DEBUG:
            logging.basicConfig(
                level=logging.DEBUG,
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
            )

        # log boot statement
        logging.debug(f"Booting @ {time()}")

        # mute pyqt logs
        logging.getLogger("PyQt6").setLevel(logging.INFO)

    def app():
        # initialize PyQt6 application
        application = QApplication(sys.argv)
        storage.application = application
        application.setStyle("Fusion")
        application.setWindowIcon(QIcon("resources/icon.ico"))

    def runner():
        # QApplication must be created before we can import ui
        app()
        import windows.constructor.main
        constructor = windows.constructor.main.Window()
        constructor.show()
        constructor.resizeEvent(None)  # trigger initial resize event

    logger()
    runner()

    # begin app event loop
    sys.exit(storage.application.exec())


if __name__ == "__main__":
    main()
