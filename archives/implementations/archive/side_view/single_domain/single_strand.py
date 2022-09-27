import workers
from PyQt6.QtWidgets import QApplication
import pyqtgraph as pg
import sys


def visualize_widget(widget):
    app = QApplication(sys.argv)
    widget.show()
    app.exec()


interior_angle_multiples = [4, 2]
switch_angle_multiples = [0]

interbase_angle = 2 * (360 / 21)
side_view = workers.plot.side_view(
    interior_angle_multiples, 3.38, interbase_angle, 12.6, 2.3
)

x_coords = side_view.x_coords(200, NEMid=True)
z_coords = side_view.z_coords(200, NEMid=True)

ui = pg.plot(
    x_coords[0][0],
    z_coords[0][0],
    title="Side View of DNA",
    symbol="o",
    symbolSize=5,
    pxMode=True,
)
ui.setAspectLocked(lock=True, ratio=50)
ui.showGrid(x=True, y=True)
ui.setWindowTitle("Side View of DNA")

visualize_widget(ui)
