from PyQt6.QtWidgets import QPushButton, QButtonGroup, QAbstractButton


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
        self.addButton(self.Juncter(), 0)
        self.addButton(self.Splicer(), 1)
        self.addButton(self.Resetter(), 2)

    def addButton(self, button: QAbstractButton, id: int) -> None:
        self.buttons.append(button)
        super().addButton(button, id)

    class Juncter(Action):
        def __init__(self):
            super().__init__("Juncter")
            self.setChecked(True)

    class Splicer(Action):
        def __init__(self):
            super().__init__("Splicer")

    class Resetter(Action):
        def __init__(self):
            super().__init__("Resetter")
