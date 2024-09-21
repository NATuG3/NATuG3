from PyQt6.QtWidgets import QButtonGroup

from natug.constants.toolbar import *
from natug.runner.managers.manager import Manager


class ToolbarManager(Manager):
    """
    Manager for the toolbar.

    Attributes:
        actions (QButtonGroup): The toolbar's actions.

    Notes:
        * self.actions.buttons[constant-for-an-action] returns the action's button
            widget.
    """

    def __init__(self, runner: "Runner"):
        self.runner = runner
        self.actions = None

    def setup(self):
        self.actions: QButtonGroup = self.runner.window.toolbar.actions
        self.actions.buttons[JUNCTER].setChecked(True)

    @property
    def current(self) -> str:
        """
        The current toolbar.

        Notes:
            See constants.modes for meanings of the various IDs.
        """
        return self.actions.checkedId()

    @current.setter
    def current(self, id_: int):
        """
        Change the current toolbar.

        Args:
            id_: The id of the toolbar to change to.
        """
        self.actions.buttons[id_].click()
