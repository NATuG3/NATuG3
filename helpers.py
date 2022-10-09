import logging

from PyQt6.QtWidgets import QMessageBox, QWidget

from contextlib import suppress

logger = logging.getLogger(__name__)


def yes_no_prompt(parent, title, msg):
    choice = QMessageBox.warning(
        parent,
        title,
        msg,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    if choice == QMessageBox.StandardButton.Yes:
        return True
    else:
        return False
