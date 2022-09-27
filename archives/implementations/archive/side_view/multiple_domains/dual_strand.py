from pprint import pprint
import workers
from PyQt6.QtWidgets import QApplication
import pyqtgraph as pg
import sys


def visualize_widget(widget):
    app = QApplication(sys.argv)
    widget.show()
    app.exec()


interior_angle_multiples = [4, 10, 6, 2, 7]
switch_angle_multiples = [0]

base_angle = 2 * (360 / 21)
side_view = workers.plot.side_view(
    interior_angle_multiples, 3.38, base_angle, 12.6, 2.3
)
x_coords = side_view.x_coords(125)
z_coords = side_view.z_coords(125)

# pprint(z_coords)
# pprint(x_coords)
# exit()

win = pg.GraphicsLayoutWidget()
win.setWindowTitle("Side View of DNA")
main_plot = win.addPlot()

for domain_index in range(side_view.domain_count):
    if domain_index % 2:  # if the domain index is an even integer
        colors = ("r", "g")
    else:
        colors = ("b", "y")

    for strand_direction in range(2):
        if strand_direction == 0:
            symbol = "t1"  # up arrow for up strand
            color = colors[0]
        elif strand_direction == 1:
            symbol = "t"  # down arrow for down strand
            color = colors[1]

        main_plot.plot(
            x_coords[domain_index][strand_direction],
            z_coords[domain_index][strand_direction],
            title="Up Strand",
            symbol=symbol,
            symbolSize=6,
            pxMode=True,
            symbolPen=color,
        )

visualize_widget(win)
