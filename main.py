import dna_nanotube_tools
from PyQt6.QtWidgets import QApplication
import pyqtgraph as pg
import sys

interior_angle_multiples = [4, 2]
switch_angle_multiples = [0]

interbase_angle = 2 * (360 / 21)
side_view = dna_nanotube_tools.plot.side_view(
    interior_angle_multiples, 3.38, interbase_angle, 12.6, 2.3
)

print(side_view.z_coords(21, NEMid=True))
