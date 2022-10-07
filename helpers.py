from PyQt6.QtWidgets import QMessageBox, QWidget
import logging


logger = logging.getLogger(__name__)


def yes_no_prompt(parent, title, msg):
    choice = QMessageBox.question(
        parent,
        title,
        msg,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    if choice == QMessageBox.StandardButton.Yes:
        return True
    else:
        return False


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
        logger.debug(
            f'Widget "{widget.objectName()}" is floating. Maximum size has been changed to (width={unbounded_width},' +
            f'"height={unbounded_height}).'
        )
    else:
        widget.setMaximumWidth(initial_width)
        widget.setMaximumHeight(initial_height)
        logger.debug(
            f'Widget "{widget.objectName()}" is no longer floating. Maximum size has been changed to ' +
            '(width={initial_width}, height={initial_height}).'
        )