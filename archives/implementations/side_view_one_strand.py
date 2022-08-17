import dna_nanotube_tools
from PyQt6.QtWidgets import QApplication
import pyqtgraph as pg
import sys

interior_angle_multiples = [4]
switch_angle_multiples = [0]

interbase_angle = 2 * (360 / 21)
side_view = dna_nanotube_tools.plot.side_view(
    interior_angle_multiples, 3.38, interbase_angle, 12.6, 2.3
)

xs_NEMid = side_view.xs(1000, NEMid=False)[0][0]
zs_NEMid = side_view.zs(1000, NEMid=False)[0][0][:-1]

ui = pg.plot(
    xs_NEMid,
    zs_NEMid,
    title="Top View of DNA",
    symbol="o",
    symbolSize=5,
    pxMode=True,
)
ui.setAspectLocked(lock=True, ratio=50)
ui.showGrid(x=True, y=True)


def visualize_widget(widget):
    app = QApplication(sys.argv)
    widget.show()
    app.exec()


widget = pg.GraphicsLayoutWidget()
widget.setWindowTitle("Side View of DNA")
visualize_widget(widget)
