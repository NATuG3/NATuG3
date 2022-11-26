from PyQt6.QtWidgets import QPushButton, QButtonGroup, QAbstractButton

from constants.toolbar import *


class Action(QPushButton):
    def __init__(self, title):
        super().__init__(title)
        self.setCheckable(True)
        self.setFixedWidth(67)


class Actions(QButtonGroup):
    def __init__(self):
        super().__init__()
        self.buttons = {}
        self.setExclusive(True)
        self._add_buttons()

    def _add_buttons(self):
        """Add all toolbar buttons to the toolbar."""
        self.add_button(self.Informer(), INFORMER)  # first button checked automatically
        self.add_button(self.Juncter(), JUNCTER)
        self.add_button(self.Nicker(), NICKER)
        self.add_button(self.Hairpinner(), HAIRPINNER)

    def add_button(self, button: QAbstractButton, id_: int) -> None:
        """
        Before calling the inherited addButton store the new button in self.buttons.

        Args:
            button: The button to add.
            id_: The id of the button to add. User set.
        """
        self.buttons[id_] = button
        super().addButton(button, id_)

    class Informer(Action):
        """Mode for obtaining information on the clicked item."""

        def __init__(self):
            super().__init__("Informer")
            self.setObjectName("Informer")

    class Juncter(Action):
        """Mode for making junctions."""

        def __init__(self):
            super().__init__("Juncter")
            self.setObjectName("Juncter")

    class Nicker(Action):
        """Mode for making nicks."""

        def __init__(self):
            super().__init__("Nicker")
            self.setObjectName("Nicker")
            self.setEnabled(False)

    class Hairpinner(Action):
        """Mode for making nicks."""

        def __init__(self):
            super().__init__("Hairpinner")
            self.setObjectName("Hairpinner")
