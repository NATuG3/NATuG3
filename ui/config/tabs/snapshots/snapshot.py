import os

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget

from ui.resources import fetch_icon


class Snapshot(QWidget):
    def __init__(self, parent: "SnapshotsPanel", filename: str) -> None:
        """
        Initialize the version item.

        Args:
            parent (VersionPanel): The parent widget.
            filename (str): The name of the version file. Not an absolute path,
                but rather the filename only.
        """
        uic.loadUi('ui/config/tabs/snapshots/snapshot.ui', self)
        super().__init__(parent)
        self.filename = filename
        self._prettify()

    @property
    def root_path(self):
        return self.parent().root_path

    def _prettify(self):
        self.remove_button.setIcon(fetch_icon('trash-outline'))
        self.remove_button.clicked.connect(self._remove_version_clicked)

        self.open_button.setIcon(fetch_icon("open-outline"))
        self.open_button.clicked.connect(self._open_version_clicked)

        self.version_name.setText(self.filename)
        self.version_name.textChanged.connect(self._version_name_changed)

    def _version_name_changed(self):
        os.rename(f"{self.root_path}/{self.filename}", self.version_name.text())
        self.filename = self.version_name.text()

    def _remove_version_clicked(self):
        self.parent().remove_version(self.filename)

    def _open_version_clicked(self):
        self.parent().load_version(self.filename)
