import sys
import ui
import json
from PyQt6.QtWidgets import QApplication
import config

config = config.load_config()
print(config.characteristic_angle)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ui.main_window()
    window.show()
    sys.exit(app.exec())
