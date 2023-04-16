import logging
import os

from PyQt6 import uic
from PyQt6.QtWidgets import QWidget

import settings
from ui.config.tabs.snapshots.snapshot import Snapshot
from ui.config.tabs.snapshots.utils import generate_snapshot_name
from ui.resources import fetch_icon

logger = logging.getLogger(__name__)


class SnapshotsPanel(QWidget):
    """
    The version panel.

    Displays a list of many state saves, and allows the user to remove them.

    Attributes:
        snapshots (list): A list of all the version widgets. Each is of type Snapshot.
        root_path (str): The root path of the version save files folder.
        loader (callable): The function to call when a version is loaded. The filepath
            to the save file is passed as the only argument.
        dumper (callable): The function to call when a version is saved. The filepath
            to the save file is passed as the only argument.
    """

    def __init__(
        self,
        parent: QWidget,
        loader: callable,
        dumper: callable,
        root_path: str = "saves/snapshots",
    ) -> None:
        """
        Initialize the version panel.

        Args:
            root_path (str): The root path of the version save files.
        """
        super().__init__(parent)
        uic.loadUi("ui/config/tabs/snapshots/panel.ui", self)

        self.snapshots = []
        self._current_snapshot = None
        self.root_path = root_path
        self.loader = loader
        self.dumper = dumper

        self._hook_signals()
        self._prettify()

        for snapshot in os.listdir(root_path):
            if snapshot.endswith(f".{settings.extension}"):
                snapshot = snapshot.split(f".{settings.extension}")[0]
                self.snapshots_list.addWidget(snapshot := Snapshot(self, snapshot))
                self.snapshots.append(snapshot)

    @property
    def current_snapshot(self) -> Snapshot | None:
        """
        The currently selected version.
        """
        return self._current_snapshot

    @current_snapshot.setter
    def current_snapshot(self, snapshot: Snapshot | None) -> None:
        if snapshot:
            if self._current_snapshot:
                self._current_snapshot.main_area.setStyleSheet("QFrame{margin: 1px;}")

            self._current_snapshot = snapshot
            snapshot.main_area.setStyleSheet(
                f"QFrame{{background-color: rgb{settings.colors['success']}}}; "
                f"margin: 1px;}}"
            )
        else:
            self._current_snapshot = None

    def previous_snapshot(self) -> Snapshot:
        """
        Obtain the previous version in the list.
        """
        if self.current_snapshot:
            index = self.snapshots.index(self.current_snapshot)
            if index != 0:
                return self.snapshots[index - 1]
            else:
                return self.snapshots[0]

    def next_snapshot(self) -> Snapshot:
        """
        Obtain the next version in the list.
        """
        if self.current_snapshot:
            index = self.snapshots.index(self.current_snapshot)
            if index != len(self.snapshots) - 1:
                return self.snapshots[index + 1]
            else:
                return self.snapshots[-1]

    def snapshot_widget(self, filename: str) -> Snapshot | None:
        """
        Get the version widget given its filename.

        Args:
            filename (str): The name of the version file. Not an absolute path,
                but rather the filename only.

        Returns:
            Snapshot: The version widget.
        """
        for snapshot in self.snapshots:
            if snapshot.filename == filename:
                return snapshot

    def take_snapshot(self, filename: str | None = None) -> None:
        """
        Add a version to the top of list.

        Args:
            filename (str): The name of the version file. Not an absolute path,
                but rather the filename only. If None, a name will be generated.
        """
        filename = filename or generate_snapshot_name(self.root_path)
        logger.debug(f"Taking snapshot: {self.root_path}/{filename}")
        if self.capacity.value() == len(self.snapshots):
            self.remove_snapshot(self.snapshots[0].filename)

        self.dumper(f"{self.root_path}/{filename}.{settings.extension}")
        self.snapshots_list.insertWidget(0, Snapshot(self, filename))

        self.snapshots.append(self.snapshots_list.itemAt(0).widget())
        self.current_snapshot = self.snapshots[-1]

    def remove_snapshot(self, filename: str) -> None:
        """
        Remove a version given its filename.

        Args:
            filename (str): The name of the version file. Not an absolute path,
                but rather the filename only.
        """
        logger.debug(f"Removing snapshot: {self.root_path}/{filename}")
        for index, snapshot in enumerate(self.snapshots):
            if snapshot.filename == filename:
                if self.current_snapshot == snapshot:
                    self.current_snapshot = None
                self.snapshots_list.removeWidget(snapshot)
                snapshot.deleteLater()
                del self.snapshots[index]
                os.remove(f"{self.root_path}/{filename}.{settings.extension}")
                break

    def load_snapshot(self, filename: str) -> None:
        """
        Load a version given its filename.

        Args:
            filename (str): The name of the version file. Not an absolute path,
                but rather the filename only.
        """
        self.loader(f"{self.root_path}/{filename}.{settings.extension}")
        self.current_snapshot = self.snapshot_widget(filename)

    def switch_to_previous(self) -> None:
        """Switch to the prior snapshot."""
        if self.snapshots.index(self.current_snapshot) != 0:
            self.load_snapshot(self.previous_snapshot().filename)

    def switch_to_next(self) -> None:
        """Switch to the next snapshot."""
        if self.snapshots.index(self.current_snapshot) != len(self.snapshots) - 1:
            self.load_snapshot(self.next_snapshot().filename)

    def _hook_signals(self):
        self.take_snapshot_button.clicked.connect(self._take_snapshot_clicked)
        self.clear_snapshots_button.clicked.connect(self._clear_snapshots_clicked)

    def _prettify(self) -> None:
        self.clear_snapshots_button.setIcon(fetch_icon("trash-outline"))

    def _clear_snapshots_clicked(self):
        for snapshot in self.snapshots.copy():
            self.remove_snapshot(snapshot.filename)

    def _take_snapshot_clicked(self):
        self.take_snapshot(generate_snapshot_name(self.root_path))
