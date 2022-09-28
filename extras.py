from functools import cache
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QIcon


@cache
def fetch_icon(name: str) -> QIcon:
    """Fetch an icon by name, and cache it."""
    return QIcon(f"application/resources/icons/{name}.svg")


def unrestrict_scale_upon_float(
    widget: QWidget,
    initial_width: int = 9999,
    unbounded_width: int = 9999,
    initial_height: int = 9999,
    unbounded_height: int = 9999,
):
    """
    Enable scaling beyond a dockable widget's normal maximum when it begins floating.

    Args:
        widget (QWidget): Widget to change size limitations upon floating/not floating of.
        initial_width (int): Maximum widget width when not floating (in pixels).
        unbounded_width (int): Maximum widget width when floating (in pixels).
        initial_height (i)nt: Maximum widget height when not floating (in pixels).
        unbounded_height (int): Maximum widget height when floating (in pixels).
    """
    if widget.isFloating():
        widget.setMaximumWidth(unbounded_width)
        widget.setMaximumHeight(unbounded_height)
    else:
        widget.setMaximumWidth(initial_width)
        widget.setMaximumHeight(initial_height)
