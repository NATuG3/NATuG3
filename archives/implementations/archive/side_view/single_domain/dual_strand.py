import workers
from PyQt6.QtWidgets import QApplication
import pyqtgraph as pg
import sys


def visualize_widget(widget):
    app = QApplication(sys.argv)
    widget.show()
    app.exec()


interior_angle_multiples = [4]
switch_angle_multiples = [0]

base_angle = 2 * (360 / 21)
side_view = workers.plot.side_view(
    interior_angle_multiples, 3.38, base_angle, 12.6, 2.3
)
xs_NEMid = side_view.x_coords(25)
zs_NEMid = side_view.z_coords(25)

win = pg.GraphicsLayoutWidget()
win.setWindowTitle("Side View of DNA")
main_plot = win.addPlot()

for strand_direction, color in enumerate(["b", "g"]):
    main_plot.plot(
        xs_NEMid[strand_direction],
        zs_NEMid[strand_direction],
        title="Up Strand",
        symbol="x",
        symbolSize=12,
        pxMode=True,
        symbolPen=color,
    )
