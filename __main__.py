from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
import sys
import database.settings
print(database.settings.presets)

if sys.platform.startswith("win"):
    # to get icon to work properly on windows this code must be run
    # https://stackoverflow.com/questions/1551605/how-to-set-applications-taskbar-icon-in-windows-7/1552105#1552105
    import ctypes

    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(__name__)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setWindowIcon(QIcon("resources/icon.ico"))
    screen = app.primaryScreen()

    import ui

    window = ui.main_window()
    window.show()
    sys.exit(app.exec())
