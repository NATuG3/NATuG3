from PyQt6.QtWidgets import QPushButton, QButtonGroup, QAbstractButton

from constants.modes import *


class Action(QPushButton):
    def __init__(self, title):
        super().__init__(title)
        self.setCheckable(True)
        self.setFixedWidth(67)


class Actions(QButtonGroup):
    def __init__(self):
        super().__init__()
        self.buttons = []
        self.setExclusive(True)
        self._add_buttons()

    def _add_buttons(self):
        """Add all toolbar buttons to the toolbar."""
        # note that the first button will be checked automatically
        self.addButton(self.Informer(), INFORMER)
        self.addButton(self.Juncter(), JUNCTER)
        self.addButton(self.Nicker(), NICKER)
        self.addButton(self.Hairpinner(), HAIRPINNER)

    def addButton(self, button: QAbstractButton, id: int) -> None:
        """Before calling the inherited addButton store the new button in self.buttons."""
        self.buttons.append(button)
        super().addButton(button, id)

    class Informer(Action):
        """Mode for obtaining information on the clicked item."""

        def __init__(self):
            super().__init__("Informer")

    class Juncter(Action):
        """Mode for making junctions."""

        def __init__(self):
            super().__init__("Juncter")

    class Nicker(Action):
        """Mode for making nicks."""

        def __init__(self):
            super().__init__("Nicker")
            self.setEnabled(False)

    class Hairpinner(Action):
        """Mode for making nicks."""

        def __init__(self):
            super().__init__("Hairpinner")
