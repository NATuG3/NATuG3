from PyQt6.QtWidgets import QToolBar, QWidget, QSizePolicy

from ui.toolbar.actions import Actions


class Toolbar(QToolBar):
    def __init__(self, parent):
        super().__init__(parent)

        self.actions = Actions()
        for button in self.actions.buttons:
            self.addWidget(button)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.addWidget(spacer)

        self._prettify()

    def _prettify(self):
        self.setFloatable(False)
        self.setMovable(False)
