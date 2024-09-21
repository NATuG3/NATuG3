import logging
import os

from natug import settings
from natug.runner.managers.manager import Manager
from natug.ui.config.tabs.snapshots import SnapshotsPanel
from natug.ui.config.tabs.snapshots.snapshot import Snapshot

logger = logging.getLogger(__name__)


class SnapshotsManager(Manager):
    """
    Manager for program snapshots.

    Attributes:
        current: The current snapshots panel.
        runner: NATuG's runner.
    """

    filepath = "saves/snapshots"

    @property
    def snapshots(self) -> list[Snapshot]:
        """
        Obtain a list of all the snapshots.

        Returns:
            A list of all the current `Snapshot`s. This is a wrapper on
                self.current.snapshots.
        """
        return self.current.snapshots

    def setup(self):
        """Load all the snapshots into the snapshots tab."""
        self.current = SnapshotsPanel(
            None,
            self.runner.load,
            self.runner.save,
            self.filepath,
        )
        for snapshot in (snapshot_files := os.listdir(self.filepath)):
            if snapshot.endswith(f".{settings.extension}"):
                snapshot = snapshot.split(f".{settings.extension}")[0]
                self.current.snapshots_list.addWidget(
                    snapshot := Snapshot(self.current, snapshot)
                )
                self.current.snapshots.append(snapshot)
        self.current.capacity.setValue(
            len(snapshot_files) + 6
            if len(snapshot_files) > 12
            else settings.default_snapshot_max_capacity
        )
        try:
            self.current.current_snapshot = self.current.snapshots[-1]
        except IndexError:
            self.current.current_snapshot = None
