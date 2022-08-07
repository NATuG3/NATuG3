import dna_nanotube_tools
from PyQt6.QtWidgets import QApplication
import sys

interior_angle_multiples = [9] * 14
switch_angle_multiples = [0] * 14


def visualize_widget(widget):
    app = QApplication(sys.argv)
    widget.show()
    app.exec()


# initilize top_view object
top_view = dna_nanotube_tools.plot.top_view(
    interior_angle_multiples, switch_angle_multiples, 2.3
)

# print out the cords
cords = top_view.cords()

# display the widget as a window
visualize_widget(top_view.ui())
