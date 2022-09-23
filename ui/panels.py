from PyQt6.QtWidgets import QWidget, QHBoxLayout
import dna_nanotube_tools.plot


class dna_views(QWidget):
    """Generate a QWidget of the two dna previews side by side."""

    def __init__(self):
        # this is an inherented class of QWidget
        # so we must initialize the parent qt widget
        super().__init__()

        # define domains to generate sideview for
        domains = [dna_nanotube_tools.domain(9, 0)] * 14

        # initilize side view class
        side_view = dna_nanotube_tools.plot.side_view(domains, 3.38, 12.6, 2.3)
        top_view = dna_nanotube_tools.plot.top_view(domains, 2.2)

        # the dna previews will be a side by side array of widgets
        dna_previews = QHBoxLayout()
        dna_previews.addWidget(side_view.ui(150))
        dna_previews.addWidget(top_view.ui())

        # convert the above dna_previews layout into an actual widget
        self.setLayout(dna_previews)
        self.show()
