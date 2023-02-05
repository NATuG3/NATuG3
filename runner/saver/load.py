import logging

from PyQt6.QtCore import QDir
from PyQt6.QtWidgets import QFileDialog

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
    assert isinstance(runner.domains.current, Domains)
    runner.domains.current.update(package.domains)
    runner.strands.current = package.strands

    # update all domains settings/dump domains
    runner.constructor.config.panel.domains.subunit_count.setValue(
        runner.domains.current.subunit.count
    )
    runner.constructor.config.panel.domains.symmetry.setValue(
        runner.domains.current.symmetry
    )
    runner.constructor.config.panel.domains.table.dump_domains(runner.domains.current)

    # refresh graphs
    runner.constructor.top_view.refresh()
    runner.constructor.side_view.refresh()
    runner.constructor.top_view.plot.autoRange()
    runner.constructor.side_view.plot.autoRange()

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
