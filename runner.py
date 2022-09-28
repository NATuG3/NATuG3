from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import sys
from time import time
import logging

# initilize logging
logging.basicConfig(
    level=logging.DEBUG,
)
# log boot statement
logging.debug(f"Booting @ {time()}")
# mute pyqt logs
logging.getLogger("PyQt6").setLevel(logging.INFO)

# initilize the database
import config

if sys.platform.startswith("win"):
    # to get icon to work properly on windows this code must be run
    # consult the below stackoverflow link for information on why
    # https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
    import ctypes

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(__name__)

if __name__ == "__main__":
    # initilize PyQt6 application
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon("resources/icon.ico"))

    # QApplication must be created before we can import ui
    import window

    # obtain and generate window item
    window = window.window()

    # show window
    window.show()

    # begin app event loop
    sys.exit(app.exec())
