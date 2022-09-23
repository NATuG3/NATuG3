import sys
import ui
import json
from PyQt6.QtWidgets import QApplication

try:
    # globalize the config in case other modules want to utilize it
    global config
    config: dict

    # load the json into config dict
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    # boot program
    if __name__ == "__main__":
        app = QApplication(sys.argv)
        window = ui.main_window()
        window.show()
        sys.exit(app.exec())

finally:
    # dump the config dict back into json file
    with open("config.json", "w") as config_file:
        json.dump(config, config_file, indent=4)
