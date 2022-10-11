import logging

from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QFileDialog

import configuration.domains.main
import configuration.domains.storage
from configuration.domains.storage import Domain
import references
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
    configuration.domains.storage.current: List[Domain] = package.domains

    # fetch the domains table in the domains tab of the config panel
    domains_table = references.constructor.configuration.tabs.domains.table
    # dump the new (updated) domains array
    domains_table.dump_domains(package.domains)

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


