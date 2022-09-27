from typing import Union
from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QDockWidget


class config(QWidget):
    """Config panel"""

    def __init__(self) -> None:
        super().__init__()
        uic.loadUi("ui/config.ui", self)

    class dockable(QDockWidget):
        def __init__(self, subself):
            super().__init__()
            # attach config panel to right dock
            subself.setWindowTitle("Config")
            subself.setStatusTip("Settings panel")
            subself.setWidget(self)
            subself.setMaximumWidth(250)
            subself.setFeatures(
                QDockWidget.DockWidgetFeature.DockWidgetFloatable
                | QDockWidget.DockWidgetFeature.DockWidgetMovable
            )
            return subself
