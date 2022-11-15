from PyQt6.QtWidgets import QButtonGroup

import refs


class _Mode:
    def __init__(self):
        self.actions: QButtonGroup = refs.constructor.toolbar.actions
        self.actions.buttons[0].setChecked(True)

    @property
    def current(self):
        """See constants.modes for meanings of the various IDs."""
        return self.actions.checkedId()
