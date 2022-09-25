from types import SimpleNamespace
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
    QDockWidget,
    QTabWidget,
    QLabel,
)
import dna_nanotube_tools
import ui.helpers, ui.panels
from PyQt6.QtCore import Qt
import database.settings

dock_areas = SimpleNamespace(left=0x1, right=0x2, top=0x4, bottom=0x8, all=0)

# START OF PLACEHOLDER CODE
domains = [dna_nanotube_tools.domain(9, 0)] * 14
# END OF PLACEHOLDER CODE


class top_view(QDockWidget):
    """Top view dock"""

    def __init__(self):
        super().__init__("Top View of Helicies")

        # preliminary window settings
        self.setWindowTitle("Top View of Helicies")
        self.setStatusTip("A plot of the top view of all domains")

        # initilize plot
        self.refresh()

        # if window is popped out sizing can be larger
        self.setMaximumWidth(250)
        self.topLevelChanged.connect(lambda: ui.helpers.float_resizer(self, 250))
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        # area for widget to be docked (this is accessed in main_window.py)
        self.area = Qt.DockWidgetArea(dock_areas.left)

    def refresh(self):
        settings = database.settings.current_preset.data
        widget = dna_nanotube_tools.plot.top_view(domains, settings.diameter)
        widget = widget.ui()
        self.setWidget(widget)
        self.widget().setStyleSheet("margin: 5px")


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

        # create reference to make coding easier
        layout = self.widget().layout()

        # container to store references to tabs in
        self.tabs = SimpleNamespace()
        self.tab_area = QTabWidget()
        # settings tab
        self.tabs.settings = ui.panels.settings()
        self.tab_area.addTab(self.tabs.settings, "Settings")
        # domains tab
        self.tabs.domains = ui.panels.domains()
        self.tab_area.addTab(self.tabs.domains, "Domains")
        # add tab area to central dock widget
        layout.addWidget(self.tab_area)

        # expanding spacer item
        layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        # add update graph button
        self.update_graphs_button = QPushButton("Overwrite Preset/Update Graphs")
        layout.addWidget(self.update_graphs_button)

        # prettification
        self.setWindowTitle("Config")
        self.setStatusTip("Settings panel")
        self.setMaximumWidth(450)

        # ensure that when the config panel is undocked it can resize to be larger
        self.topLevelChanged.connect(
            lambda: ui.helpers.float_resizer(self, 250, maximum_width=400)
        )

        # prevent closing the panel
        self.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetFloatable
            | QDockWidget.DockWidgetFeature.DockWidgetMovable
        )

        # area for widget to be docked (this is accessed in main_window.py)
        self.area = Qt.DockWidgetArea(dock_areas.right)
