from PyQt6.QtWidgets import QMenuBar


class Menubar(QMenuBar):
    def __init__(self):
        super().__init__()

        from constructor.menubar import File, View, Help

        self.addMenu(File(self))
        self.addMenu(View(self))
        self.addMenu(Help(self))
