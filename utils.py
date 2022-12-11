import logging
import subprocess
from functools import wraps

from PyQt6.QtWidgets import QMessageBox

import constants

logger = logging.getLogger(__name__)


def show_in_file_explorer(filepath):
    """Open the filepath in the file explorer."""
    logger.info(f'Opening "{filepath}" in file explorer.')
    subprocess.Popen(f'explorer /select, "{filepath}"')


def bases_only(blended: str):
    """Take an input string and return a version with only bases."""
    new_bases = []
    for potential_base in blended:
        if potential_base.upper() in constants.bases.DNA or potential_base == " ":
            new_bases.append(potential_base.upper())
    return "".join(new_bases)


def singleton(orig_cls):
    """Decorator to convert a class instance into a singleton."""
    # https://igeorgiev.eu/python/design-patterns/python-singleton-pattern-decorator/

    orig_new = orig_cls.__new__
    instance = None

    @wraps(orig_cls.__new__)
    def __new__(cls, *args, **kwargs):
        nonlocal instance  # we are referring to the above instance variable
        if (
                instance is None
        ):  # if there is no instance of the class already than create one
            instance = orig_new(cls, *args, **kwargs)
        return instance  # return class instance

    orig_cls.__new__ = __new__
    return orig_cls


def factors(number):
    # https://www.programiz.com/python-programming/examples/factor-number
    output = []
    for i in range(1, number + 1):
        if number % i == 0:
            output.append(i)
    return output


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


def warning(parent, title, msg):
    QMessageBox.critical(
        parent,
        title,
        msg,
        QMessageBox.StandardButton.Ok,
    )


def reverse_hidenness(potentially_hidden_item):
    """Reverse the hiddenness of a widget"""
    if potentially_hidden_item.isHidden():
        potentially_hidden_item.show()
    else:
        potentially_hidden_item.hide()


def inverse(integer: int) -> int:
    """
    Returns int(not bool(integer)).

    Args:
        integer: Either 0 or 1.

    Returns:
        int: 0 or 1.
    """
    return int(not bool(integer))
