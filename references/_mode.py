from PyQt6.QtWidgets import QButtonGroup

import references
from constructor.toolbar.actions import Actions


class _Mode:
    def __init__(self):
        self.actions: QButtonGroup = references.constructor.toolbar.actions
        self.actions.buttons[0].setChecked(True)

    @property
    def current(self):
        """See constants.modes for meanings of the various IDs."""
        self.actions.checkedId()
