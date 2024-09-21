import os

from PyQt6.QtWidgets import QWidget
from PyQt6 import uic

from natug import settings, utils
from natug.ui.resources import fetch_icon


class Snapshot(QWidget):
    def __init__(self, parent: "SnapshotsPanel", filename: str) -> None:
        """
        Initialize the snapshot item.

        Args:
            parent (SnapshotPanel): The parent widget.
            filename (str): The name of the snapshot file. Not an absolute path,
                but rather the filename only.
        """
        super().__init__()
        uic.loadUi("./ui/config/tabs/snapshots/snapshot.ui", self)
        self.parent = parent
        self.filename = filename
        self._prettify()
        self._hook_signals()

    @property
    def root_path(self):
        return self.parent.root_path

    def _prettify(self):
        self.remove_button.setIcon(fetch_icon("trash-outline"))
        self.open_button.setIcon(fetch_icon("download-outline"))
        self.snapshot_name.setText(self.filename)

    def _hook_signals(self):
        self.snapshot_name.editingFinished.connect(self._snapshot_name_changed)
        self.remove_button.clicked.connect(self._remove_snapshot_clicked)
        self.open_button.clicked.connect(self._open_snapshot_clicked)

    def _snapshot_name_changed(self):
        if self.snapshot_name.text() not in self.parent.snapshot_filenames:
            os.rename(
                f"{self.root_path}/{self.filename}.{settings.extension}",
                f"{self.root_path}/{self.snapshot_name.text()}.{settings.extension}",
            )
            self.filename = self.snapshot_name.text()
        else:
            self.snapshot_name.setText(self.filename)
            utils.warning(
                self,
                "Snapshot name exists",
                "A snapshot with that name already exists. Please choose another name.",
            )

    def _remove_snapshot_clicked(self):
        self.parent.remove_snapshot(self.filename)

    def _open_snapshot_clicked(self):
        self.parent.load_snapshot(self.filename)
