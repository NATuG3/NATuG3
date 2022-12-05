from PyQt6.QtWidgets import QButtonGroup

import refs
from constants.toolbar import *


class _Toolbar:
    def __init__(self):
        self.actions: QButtonGroup = refs.constructor.toolbar.actions
        self.actions.buttons[JUNCTER].setChecked(True)

    @property
    def current(self) -> str:
        """
        The current toolbar toolbar.

        Notes:
            See constants.modes for meanings of the various IDs.
        """
        return self.actions.checkedId()

    @current.setter
    def current(self, id_: int):
        """
        Change the current toolbar toolbar.

        Args:
            id_: The id of the toolbar to change to.
        """
        self.actions.buttons[id_].click()
