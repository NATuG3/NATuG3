import os

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget

from ui.resources import fetch_icon


class Snapshot(QWidget):
    def __init__(self, parent: "SnapshotsPanel", filename: str) -> None:
        """
        Initialize the snapshot item.

        Args:
            parent (SnapshotPanel): The parent widget.
            filename (str): The name of the snapshot file. Not an absolute path,
                but rather the filename only.
        """
        super().__init__(parent)
        uic.loadUi('ui/config/tabs/snapshots/snapshot.ui', self)
        self.filename = filename
        self._prettify()

    @property
    def root_path(self):
        return self.parent().root_path

    def _prettify(self):
        self.remove_button.setIcon(fetch_icon('trash-outline'))
        self.remove_button.clicked.connect(self._remove_snapshot_clicked)

        self.open_button.setIcon(fetch_icon("download-outline"))
        self.open_button.clicked.connect(self._open_snapshot_clicked)

        self.snapshot_name.setText(self.filename)
        self.snapshot_name.textChanged.connect(self._snapshot_name_changed)

    def _snapshot_name_changed(self):
        os.rename(f"{self.root_path}/{self.filename}", self.snapshot_name.text())
        self.filename = self.snapshot_name.text()

    def _remove_snapshot_clicked(self):
        self.parent().remove_snapshot(self.filename)

    def _open_snapshot_clicked(self):
        self.parent().load_snapshot(self.filename)
