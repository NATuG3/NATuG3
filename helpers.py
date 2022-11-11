import logging
from functools import wraps, cache
from typing import Literal

from PyQt6.QtGui import QFont, QPainterPath, QTransform
from PyQt6.QtWidgets import QMessageBox

logger = logging.getLogger(__name__)


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


@cache
def custom_symbol(symbol: str, font: QFont = QFont("San Serif")):
    """Create custom symbol with font for pyqtgraph."""
    # https://stackoverflow.com/a/70789822
    pg_symbol = QPainterPath()
    pg_symbol.addText(0, 0, font, symbol)
    br = pg_symbol.boundingRect()
    scale = min(1.0 / br.width(), 1.0 / br.height())
    tr = QTransform()
    tr.scale(scale, -scale)
    tr.translate(-br.x() - br.width() / 2.0, -br.y() - br.height() / 2.0)
    return tr.map(pg_symbol)
