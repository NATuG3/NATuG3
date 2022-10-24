from types import SimpleNamespace

from PyQt6.QtWidgets import QMenu

import runner
import runner.saver
from resources import fetch_icon


class File(QMenu):
    def __init__(self, parent):
        super().__init__("&File", parent)

        # container for actions
        self.actions = SimpleNamespace()

        # file -> open
        open_ = self.actions.open = self.addAction("Open")
        open_.setIcon(fetch_icon("open-outline"))
        open_.setShortcut("ctrl+o")
        open_.setStatusTip("Open saved stage from file")
        open_.triggered.connect(lambda: runner.saver.load.runner(parent))

        # file -> save
        save = self.actions.save = self.addAction("Save")
        save.setIcon(fetch_icon("save-outline"))
        save.setShortcut("ctrl+s")
        save.setStatusTip("Save current stage top file")
        save.triggered.connect(lambda: runner.saver.save.runner(parent))
