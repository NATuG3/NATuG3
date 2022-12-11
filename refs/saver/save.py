import logging
import pickle

from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QFileDialog

import structures
from utils import show_in_file_explorer

logger = logging.getLogger(__name__)


def runner(parent):
    """Initiate save process flow."""
    # create file selector for save
    selector = FileSelector(parent)

    # run worker(filepath) after file has been chosen
    selector.accepted.connect(lambda: worker(selector.selectedFiles()[0]))


def worker(filepath):
    """Runs after filepath has been chosen."""

    # obtain save package
    package = structures.misc.Save()

    # dump save object to filepath
    with open(filepath, "wb") as file:
        pickle.dump(package, file)

    # log the save
    logger.info(f"Created save @ {filepath}.")

    # open the saved path in file explorer
    show_in_file_explorer(filepath)


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
