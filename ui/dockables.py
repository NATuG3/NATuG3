from types import SimpleNamespace
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QVBoxLayout,
    QTabWidget,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QDockWidget,
)
from PyQt6 import uic
import dna_nanotube_tools
import ui.slots, ui.panels
from PyQt6.QtCore import Qt

# START OF PLACEHOLDER CODE
domains = [dna_nanotube_tools.domain(9, 0)] * 14
_top_view = dna_nanotube_tools.plot.top_view(domains, 2.2)
# END OF PLACEHOLDER CODE

dock_areas = SimpleNamespace(left=0x1, right=0x2, top=0x4, bottom=0x8, all=0)


class top_view(QDockWidget):
    """Top view dock"""

    def __init__(self):
        super().__init__("Top View of Helicies")

        self.setWindowTitle("Top View of Helicies")
        self.setStatusTip("A plot of the top view of all domains")
        self.setWidget(_top_view.ui())
        self.widget().setStyleSheet("margin: 5px")

        self.setMaximumWidth(250)
        self.topLevelChanged.connect(lambda: ui.slots.float_resizer(self, 250))
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        # area for widget to be docked (this is accessed in main_window.py)
        self.area = Qt.DockWidgetArea(dock_areas.left)


class config(QDockWidget):
    """
    A tab box for config and domain configuration.

    This is a docked widget which initiates on the right side of the main window.
    The layout() subclass arranges all the other subclasses in this order (top to bottom):
    """

    def __init__(self) -> None:
        super().__init__()

        self.setWidget(
            QWidget()
        )  # main widget is empty widget with vertical array layout
        self.widget().setLayout(QVBoxLayout())  # add layout to empty widget
        layout = self.widget().layout()  # create reference to make coding easier

        # main tab area
        self.tab_area = QTabWidget()
        self.tab_area.addTab(ui.panels.settings(), "Settings")
        self.tab_area.addTab(ui.panels.domains(), "Domains")
        layout.addWidget(self.tab_area)

        # expanding spacer item
        layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        # update graphs button
        self.update_graphs_button = QPushButton("Update Graphs")
        layout.addWidget(self.update_graphs_button)

        # prettification
        self.setWindowTitle("Config")
        self.setStatusTip("Settings panel")
        self.setMaximumWidth(450)

        # ensure that when the config panel is undocked it can resize to be larger
        self.topLevelChanged.connect(
            lambda: ui.slots.float_resizer(self, 250, maximum_width=400)
        )

        # prevent closing the panel
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        # area for widget to be docked (this is accessed in main_window.py)
        self.area = Qt.DockWidgetArea(dock_areas.right)
