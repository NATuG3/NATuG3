import logging
from typing import Literal

from PyQt6.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)


def confirm(parent, title, msg):
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


def reverse_hidenness(potentially_hidden_item):
    """Reverse the hiddenness of a widget"""
    if potentially_hidden_item.isHidden():
        potentially_hidden_item.show()
    else:
        potentially_hidden_item.hide()


def inverse(integer: Literal[0, 1]) -> Literal[1, 0]:
    """
    Returns int(not bool(integer)).

    Args:
        integer (Literal[0, 1]): Either 0 or 1.

    Returns:
        int: 0 or 1.
    """
    return int(not bool(integer))
