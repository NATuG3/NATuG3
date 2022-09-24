from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QVBoxLayout
from PyQt6 import uic
import dna_nanotube_tools.plot
import database

class title_panel(QWidget):
    def __init__(self):
        # this is an inherented class of QWidget
        # so we must initialize the parent qt widget
        super().__init__()

        self.setLayout(QVBoxLayout())

        # add title widget
        self.layout().addWidget(QLabel("<h1>DNA Nanotube Constructor</h1>"))
        self.layout().addWidget(
            QLabel("<p>Created by Wolf Mermelstein and William Sherman</p>")
        )


class dna_views(QWidget):
    def __init__(self):
        # this is an inherented class of QWidget
        # so we must initialize the parent qt widget
        super().__init__()

        # START OF PLACEHOLDER CODE
        domains = [dna_nanotube_tools.domain(9, 0)] * 14
        side_view = dna_nanotube_tools.plot.side_view(domains, 3.38, 12.6, 2.3)
        top_view = dna_nanotube_tools.plot.top_view(domains, 2.2)
        # END OF PLACEHOLDER CODE

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(side_view.ui(150))
        self.layout().addWidget(top_view.ui())


class configuration(QWidget):
    def __init__(self) -> None:
        # this is an inherented class of QWidget
        # so we must initialize the parent qt widget
        super().__init__()
        # load the widget from the ui file
        uic.loadUi("ui/config.ui", self)

        loaded_config = database.load()

        # set saved values of each setting and hook it to config updating
        self.strandSwitchDistance_input.valueChanged.connect(
            lambda: database.update(
                "strand_switch_distance", self.strandSwitchDistance_input
            )
        )
        self.strandSwitchDistance_input.setValue(loaded_config["strand_switch_distance"])
        
        self.strandSwitchAngle_input.valueChanged.connect(
            lambda: database.update("strand_switch_angle", self.strandSwitchAngle_input.value())
        )
        self.strandSwitchAngle_input.setValue(loaded_config["strand_switch_angle"])

        self.domainDistance_input.valueChanged.connect(
            lambda: database.update("domain_distance", self.domainDistance_input.value())
        )
        self.domainDistance_input.setValue(loaded_config["domain_distance"])

        self.NEMidHeight_input.valueChanged.connect(
            lambda: database.update("NEMid_height", self.NEMidHeight_input.value())
        )
        self.NEMidHeight_input.setValue(loaded_config["NEMid_height"])

        self.generateCount_input.valueChanged.connect(
            lambda: database.update("generate_count", self.generateCount_input.value())
        )
        self.generateCount_input.setValue(loaded_config["generate_count"])

        self.characteristicAngle_input.valueChanged.connect(
            lambda: database.update("characteristic_angle", self.characteristicAngle_input.value())
        )
        self.characteristicAngle_input.setValue(loaded_config["characteristic_angle"])
