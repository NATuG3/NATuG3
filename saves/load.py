import logging

from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QFileDialog

import config.domains.main
import config.domains.storage
from config.domains.storage import Domain
import storage
import saves.datatypes

from typing import List

logger = logging.getLogger(__name__)


def runner(parent):
    """Initiate save process flow."""
    selector = FileSelector(parent)
    selector.accepted.connect(lambda: worker(selector.selectedFiles()[0]))


def worker(filename):
    """Runs after filename has been chosen."""

    # load save package from chosen filename
    package = saves.datatypes.Save.from_file(filename)

    # update the current domains array
    config.domains.storage.current: List[Domain] = package.domains

    # update all domains settings/dump domains
    storage.windows.constructor.config.tabs.domains.subunit_count.setValue(
        config.domains.storage.current.subunit.count
    )
    storage.windows.constructor.config.tabs.domains.symmetry.setValue(
        config.domains.storage.current.symmetry
    )
    storage.windows.constructor.config.tabs.domains.table.dump_domains(
        config.domains.storage.current.subunit.domains
    )

    logger.info(f"Loaded save @{filename}.")


class FileSelector(QFileDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent, caption="Choose location to save file")

        # store parent reference
        self.parent = parent

        # file dialog is of the AcceptSave type
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)

        # allow user to choose files that exist only
        self.setFileMode(QFileDialog.FileMode.ExistingFile)

        # only let user choose files
        self.setFilter(QDir.Filter.Files)

        # only allow .nano files
        self.setNameFilter("*.nano")

        # forces the appending of .nano
        self.setDefaultSuffix(".nano")

        # begin flow
        self.show()
