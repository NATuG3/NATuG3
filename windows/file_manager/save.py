from PyQt6.QtWidgets import QFileDialog, QDialog
from PyQt6.QtCore import QDir
from PyQt6 import uic


# saving flow:
#   1) runner() creates file dialog and has user choose file location
#   2) runner() creates Window(QDialog) for save settings
#   3) Window has "save" button which completes the save, or "cancel" button to cancel


def runner(parent):
    # create file selector
    file_selector = FileSelector(parent)
    # show file selector
    file_selector.show()
    file_selector.finished.connect(lambda: Saver(file_selector.selectedFiles()[0]))


class FileSelector(QFileDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent, caption="Choose location to save file")

        # store parent reference
        self.parent = parent

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


class Saver(QDialog):
    def __int__(self, filepath) -> None:
        super().__init__()

        uic.loadUi("windows/file_manager/save.ui", self)

        self.set

        self.show()
