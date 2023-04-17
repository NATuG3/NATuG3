import logging
import os

import settings
from ui.config.tabs.snapshots import SnapshotsPanel
from ui.config.tabs.snapshots.snapshot import Snapshot

logger = logging.getLogger(__name__)


class SnapshotsManager:
    """
    Manager for program snapshots.

    Attributes:
        current: The current snapshots panel.
        runner: NATuG's runner.
    """

    filepath = "saves/snapshots"

    def __init__(self, runner: "Runner"):
        """
        Initialize the snapshots manager.

        Args:
            runner: NATuG's runner.
        """
        self.current = None
        self.runner = runner

    @property
    def snapshots(self) -> list[Snapshot]:
        """Return a list of all the snapshots."""
        return self.current.snapshots

    def setup(self):
        """Set up the snapshots module."""
        self.current = SnapshotsPanel(
            None, self.runner.load, self.runner.save, self.filepath
        )
        for snapshot in (snapshot_files := os.listdir(self.filepath)):
            if snapshot.endswith(f".{settings.extension}"):
                snapshot = snapshot.split(f".{settings.extension}")[0]
                self.current.snapshots_list.addWidget(
                    snapshot := Snapshot(self, snapshot)
                )
                self.current.snapshots.append(snapshot)
        self.current.capacity.setValue(
            len(snapshot_files) + 6 if len(snapshot_files) > 12 else
            settings.default_snapshot_max_capacity
        )
        self.current.take_snapshot()
