from PyQt6.QtWidgets import QPushButton, QButtonGroup, QAbstractButton

from constants.toolbar import *


class Action(QPushButton):
    """
    A singular action parent class for the toolbar.

    Actions are modified QPushButtons that are checkable (toggleable), and have a fixed width.
    """
    def __init__(self, title):
        super().__init__(title)
        self.setCheckable(True)
        self.setFixedWidth(67)


class Actions(QButtonGroup):
    """
    Set up all the actions for the toolbar.

    Actions are mutually exclusive; only one can be active at a time.
    """

    def __init__(self):
        """Initialize the QButtonGroup."""
        super().__init__()
        self.buttons = {}
        self.setExclusive(True)
        self._add_buttons()

    def _add_buttons(self):
        """Add all toolbar buttons to the toolbar."""
        self.add_button(self.Informer(), INFORMER)
        self.add_button(self.Juncter(), JUNCTER)
        self.add_button(self.Nicker(), NICKER)
        self.add_button(self.Hairpinner(), HAIRPINNER)
        self.add_button(self.Highlighter(), HIGHLIGHTER)

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

    class Hairpinner(Action):
        """Mode for making nicks."""

        def __init__(self):
            super().__init__("Hairpinner")
            self.setObjectName("Hairpinner")

    class Highlighter(Action):
        """Mode for highlighting items."""

        def __init__(self):
            super().__init__("Highlighter")
            self.setObjectName("Highlighter")