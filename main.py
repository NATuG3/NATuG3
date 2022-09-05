import dna_nanotube_tools
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
import sys

# define domains to generate sideview for
interjunction_multiples = [9] * 14
domains = [
    dna_nanotube_tools.domain(interjunction_multiple, 0)
    for interjunction_multiple in interjunction_multiples
]

# initilize side view class
side_view = dna_nanotube_tools.plot.side_view(domains, 3.38, 12.6, 2.3)
top_view = dna_nanotube_tools.plot.top_view(domains, 2.2)
print("Initilized preview classes")

# create ui widget
side_view_ui_widget = side_view.ui(100)
top_view_ui_widget = top_view.ui()
print("Created UI widgets/preview data")

# display the widgets side-by-side
app = QApplication(sys.argv)
print("Created app")

window = QWidget()  # set up window as a widget
window.setWindowTitle("DNA Visualizer")

layout = QHBoxLayout()  # initilize side-by-side layout
layout.addWidget(side_view_ui_widget)  # add the side view to the left
layout.addWidget(top_view_ui_widget)  # add the top view to the right
window.setLayout(layout)  # apply the side-by-side layout to the window
window.show()  # show the duel-widget window

sys.exit(app.exec_())  # run app's main event loop
