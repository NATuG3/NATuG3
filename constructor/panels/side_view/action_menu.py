from PyQt6.QtWidgets import QPushButton, QHBoxLayout, QWidget, QSpacerItem, QSizePolicy


class Action(QPushButton):
    def __init__(self, title):
        super().__init__(title)
        self.setFixedWidth(50)


class Actions:
    class Juncter(Action):
        def __init__(self):
            super().__init__("Juncter")

    class Splicer(Action):
        def __init__(self):
            super().__init__("Splicer")

    class Resetter(Action):
        def __init__(self):
            super().__init__("Resetter")


class ActionMenu(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setLayout(QHBoxLayout())

        self.layout().addWidget(Actions.Juncter())
        self.layout().addWidget(Actions.Splicer())
        self.layout().addWidget(Actions.Resetter())
        self.layout().addItem(QSpacerItem(0, 0, hPolicy=QSizePolicy.Policy.Expanding))
