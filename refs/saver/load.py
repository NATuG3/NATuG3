import logging

from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QFileDialog

import refs
from structures.domains import Domains
from structures.misc.save import Save

logger = logging.getLogger(__name__)


def runner(parent):
    """Initiate save process flow."""
    selector = FileSelector(parent)
    selector.accepted.connect(lambda: worker(selector.selectedFiles()[0]))


def worker(filepath):
    """Runs after filepath has been chosen."""

    # load save package from chosen filepath
    package = Save.from_file(filepath)

    # update the current domains array
    assert isinstance(refs.domains.current, Domains)
    refs.domains.current = package.domains
    refs.strands.current = package.strands

    # update all domains settings/dump domains
    refs.constructor.config.panel.tabs.domains.subunit_count.setValue(
        refs.domains.current.subunit.count
    )
    refs.constructor.config.panel.tabs.domains.symmetry.setValue(
        refs.domains.current.symmetry
    )
    refs.constructor.config.panel.tabs.domains.table.dump_domains(refs.domains.current)

    # refresh graphs
    refs.constructor.top_view.refresh()
    refs.constructor.side_view.refresh()
    refs.constructor.top_view.plot.autoRange()
    refs.constructor.side_view.plot.autoRange()

    logger.info(f"Loaded save @ {filepath}.")


class FileSelector(QFileDialog):
    def __init__(self, parent) -> None:
        super().__init__(parent, caption="Choose location to save file")

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
