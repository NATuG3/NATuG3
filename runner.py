from PyQt6.QtWidgets import QApplication
import sys
import database
import ui

config = database.config()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ui.main_window()
    window.show()
    sys.exit(app.exec())