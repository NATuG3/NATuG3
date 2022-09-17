import dna_nanotube_tools
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication
import sys

"""
Generate and display an overhead (top view) of double helicies.
"""


def visualize_widget(widget):
    app = QApplication(sys.argv)
    widget.show()
    app.exec()


# define domains to generate topview for
domains = [dna_nanotube_tools.domain(9, 0) for i in range(14)]

# generate top view data
top_view = dna_nanotube_tools.plot.top_view(domains, 2.2)

# obtain coords
u_coords = top_view.u_coords
v_coords = top_view.v_coords

widget = pg.plot(
    u_coords,
    v_coords,
    title="Top View of DNA",
    symbol="o",
    symbolSize=80,
    pxMode=True,
)
widget.setAspectLocked(lock=True, ratio=1)
widget.showGrid(x=True, y=True)
visualize_widget(widget)
