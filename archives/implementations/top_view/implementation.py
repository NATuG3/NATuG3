import dna_nanotube_tools
import pyqtgraph as pg

"""
Generate and display an overhead (top view) of double helicies.
"""

# define domains to generate topview for
domains = [dna_nanotube_tools.domain(4, 0) * 14]

# generate top view data
top_view = dna_nanotube_tools.plot.top_view(domains, 2.2)

# obtain coords
u_coords = top_view.u_coords
v_coords = top_view.v_coords

ui_widget = pg.plot(
    u_coords,
    v_coords,
    title="Top View of DNA",
    symbol="o",
    symbolSize=80,
    pxMode=True,
)
ui_widget.setAspectLocked(lock=True, ratio=1)
ui_widget.showGrid(x=True, y=True)