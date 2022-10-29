import logging

from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QFileDialog

import references
from datatypes.domains import Domains
from datatypes.misc.save import Save

logger = logging.getLogger(__name__)


def runner(parent):
    """Initiate save process flow."""
    selector = FileSelector(parent)
    selector.accepted.connect(lambda: worker(selector.selectedFiles()[0]))


def worker(filename):
    """Runs after filename has been chosen."""

    # load save package from chosen filename
    package = Save.from_file(filename)

    # update the current domains array
    assert isinstance(references.domains.current, Domains)
    references.domains.current = package.domains
    references.strands = package.strands

    # update all domains settings/dump domains
    references.constructor.config.panel.tabs.domains.subunit_count.setValue(
        references.domains.current.subunit.count
    )
    references.constructor.config.panel.tabs.domains.symmetry.setValue(
        references.domains.current.symmetry
    )
    references.constructor.config.panel.tabs.domains.table.dump_domains(
        references.domains.current.subunit.domains
    )

    # refresh graphs
    references.constructor.top_view.refresh()
    references.constructor.side_view.refresh()

    logger.info(f"Loaded save @ {filename}.")


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
