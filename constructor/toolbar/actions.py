from PyQt6.QtWidgets import QPushButton, QButtonGroup, QAbstractButton

from constants.modes import *


class Action(QPushButton):
    def __init__(self, title):
        super().__init__(title)
        self.setCheckable(True)
        self.setFixedWidth(50)


class Actions(QButtonGroup):
    def __init__(self):
        super().__init__()
        self.buttons = []
        self.setExclusive(True)
        self._add_buttons()

    def _add_buttons(self):
        self.addButton(self.Juncter(), JUNCTER)
        self.addButton(self.Splicer(), SPLICER)
        self.addButton(self.Resetter(), RESETTER)

    def addButton(self, button: QAbstractButton, id: int) -> None:
        self.buttons.append(button)
        super().addButton(button, id)

    class Juncter(Action):
        def __init__(self):
            super().__init__("Juncter")

    class Splicer(Action):
        def __init__(self):
            super().__init__("Splicer")

    class Resetter(Action):
        def __init__(self):
            super().__init__("Resetter")
