import dna_nanotube_tools
from PyQt6.QtWidgets import QApplication
import sys


def visualize_widget(widget):
    app = QApplication(sys.argv)
    widget.show()
    app.exec()


# domain-object-instances of all the domains
domains = [dna_nanotube_tools.domain(9, 0) for i in range(14)]
# distance between domains
domain_distance = 2.3

# initilize top_view object
output = dna_nanotube_tools.plot.top_view(domains, domain_distance)
# display the widget as a window
visualize_widget(output.ui_widget)
