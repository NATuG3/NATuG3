import math
import sys
import pyqtgraph as pg
from PyQt6.QtWidgets import QApplication

theta_c = 360/21
theta_s = 126
d = 2.3

m_c = [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9]
m_s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# m_c = [6, 7, 7, 7, 7, 7, 7, 0, 0, 0]
# m_s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

class topView():
    """
    Generate (u, v) cords for topview of helicies generation.
    """

    def __init__(self, m_c, m_s) -> None:
        if len(m_c) != len(m_s):
            raise ValueError("Input lengths don't match")

        self.m_c = m_c
        self.m_s = m_s

        self.psi_list = [0]

        self.u_list = [0]
        self.v_list = [0]

    def theta_by_index(self, index: int) -> float:
        return (self.m_c[index-1] * theta_c) - (self.m_s[index-1] * theta_s)

    def psi_by_index(self, index: int) -> float:
        try:
            return self.psi_list[index]
        except IndexError:
            while len(self.psi_list) < index:
                self.psi_list.append(
                    self.psi_list[-1] + 180-self.theta_by_index(len(self.psi_list)+1)
                )
            return self.psi_list[-1]

    def u_by_index(self, index: int) -> float:
        index += 1
        try:
            return self.u_list[index]
        except IndexError:
            if index == 1: return 0
            while len(self.u_list) < index:
                self.u_list.append(
                    self.u_list[-1] + d * math.cos(
                        math.radians(self.psi_by_index(len(self.u_list)))
                    )
                )
            return self.u_list[-1]
    
    def v_by_index(self, index: int) -> float:
        try:
            return self.v_list[index]
        except IndexError:
            if index == 1: return 0
            while len(self.v_list) < index:
                self.v_list.append(
                    self.v_list[-1] + d * math.sin(
                        math.radians(self.psi_by_index(len(self.v_list)))
                    )
                )
            return self.v_list[-1]

generator = topView(m_c, m_s)

u = [round(generator.u_by_index(i), 4) for i in range(len(m_c)+1)]
v = [round(generator.v_by_index(i), 4) for i in range(len(m_c)+1)]
print(u)
print(v)

# pen=None to hide pen
ploted = pg.plot(u, v, title="Top View of DNA", symbol='o', symbolSize=80, pxMode=True)
ploted.showGrid(x=True, y=True)

app = QApplication(sys.argv)

ploted.show()

app.exec()