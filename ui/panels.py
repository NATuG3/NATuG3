from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QSplitter, QGroupBox
from PyQt6 import uic
import dna_nanotube_tools.plot

class title_panel(QWidget):
    def __init__(self):
        # this is an inherented class of QWidget
        # so we must initialize the parent qt widget
        super().__init__()

        self.setLayout(QVBoxLayout())

        # add title widget
        title = QLabel("""<h1>DNA Nanotube Constructor</h1>""")
        self.layout().addWidget(title)

class configuration(QGroupBox):
    def __init__(self) -> None:
        # this is an inherented class of QWidget
        # so we must initialize the parent qt widget
        super().__init__()
        # load the widget from the ui file
        uic.loadUi("ui/config.ui", self)
        self.setTitle("Settings")
        self.setMaximumWidth(170)

class central_panel(QSplitter):
    def __init__(self):
        # this is an inherented class of QWidget
        # so we must initialize the parent qt widget
        super().__init__()

        # START OF PLACEHOLDER CODE
        domains = [dna_nanotube_tools.domain(9, 0)] * 14
        side_view = dna_nanotube_tools.plot.side_view(domains, 3.38, 12.6, 2.3)
        top_view = dna_nanotube_tools.plot.top_view(domains, 2.2)
        # END OF PLACEHOLDER CODE

        self.addWidget(side_view.ui(150))
        self.addWidget(top_view.ui())
        self.addWidget(configuration())

        self.setHandleWidth(8)