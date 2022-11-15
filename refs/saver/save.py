import logging
import pickle

from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QFileDialog

import structures

logger = logging.getLogger(__name__)


def runner(parent):
    """Initiate save process flow."""
    # create file selector for save
    selector = FileSelector(parent)

    # run worker(filename) after file has been chosen
    selector.accepted.connect(lambda: worker(selector.selectedFiles()[0]))


def worker(filename):
    """Runs after filename has been chosen."""

    # obtain save package
    package = structures.misc.Save()

    # dump save object to filename
    with open(filename, "wb") as file:
        pickle.dump(package, file)

    # log the save
    logger.info(f"Created save @ {filename}.")


class FileSelector(QFileDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent, caption="Choose location to save file")

        # file dialog is of the AcceptSave type
        self.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)

        # allow user to choose files that do not exist
        self.setFileMode(QFileDialog.FileMode.AnyFile)

        # only let user choose writable files
        self.setFilter(QDir.Filter.Files)

        # only allow .nano files
        self.setNameFilter("*.nano")

        # forces the appending of .nano
        self.setDefaultSuffix(".nano")

        # begin flow
        self.show()
