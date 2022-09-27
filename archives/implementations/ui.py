import workers.graph
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
import sys

# define domains to generate sideview for
interjunction_multiples = (7, 7, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0)
domains = [
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
    workers.domain(9, 0),
]

# initilize side view class
side_view = workers.graph.side_view(domains, 3.38, 12.6, 2.3)
top_view = workers.graph.top_view(domains, 2.2)

# create ui widget
side_view_ui_widget = side_view.ui(150)
top_view_ui_widget = top_view.ui()

# display the widgets side-by-side
app = QApplication(sys.argv)

window = QWidget()  # set up window as a widget
window.setWindowTitle("DNA Visualizer")

layout = QHBoxLayout()  # initilize side-by-side layout
layout.addWidget(side_view_ui_widget)  # add the side view to the left
layout.addWidget(top_view_ui_widget)  # add the top view to the right

window.setLayout(layout)  # apply the side-by-side layout to the window
window.show()  # show the duel-widget window

sys.exit(app.exec_())  # run app's main event loop
