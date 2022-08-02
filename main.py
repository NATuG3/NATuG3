import dna_nanotube_tools
from PyQt6.QtWidgets import QApplication
import sys

m_c = [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9]
m_s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
generated_top_view = dna_nanotube_tools.top_view(m_c, m_s, 2.3)

# print out the cords
cords = generated_top_view.cords()
cords = [(round(u, 2), round(v, 2)) for u, v in cords]
print(cords)

# display the widget as a window
app = QApplication(sys.argv)
ui = generated_top_view.ui()
ui.show()
app.exec()
