import math
# import sys
# import pyqtgraph as pg
# from PyQt6.QtWidgets import QApplication

theta_c = 360/21
theta_s = 126
d = 2.3

# m_c = [9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9]
# m_s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
m_c = [6, 7, 7, 7, 7, 7, 7, 0, 0, 0]
m_s = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

class topView():
    """
    Generate (u, v) cords for topview of helicies generation.
    """

    def __init__(self, m_c, m_s) -> None:
        if len(m_c) != len(m_s):
            raise ValueError("Input lengths don't match")

        self.inputLength = len(m_c)

        self.m_c = m_c
        self.m_s = m_s

        self.psi_list = [0]
        self.theta_list = []

        self.u_list = [0]
        self.v_list = [0]

        self.thetas()
        self.psis()
        self.us()
        self.vs()

    def theta_by_index(self, index: int) -> float:
        return (self.m_c[index-1] * theta_c) - (self.m_s[index-1] * theta_s)

    def thetas(self):
        current = 1
        while len(self.theta_list) < self.inputLength:
            self.theta_list.append(
                (self.m_c[current-1] * theta_c) - (self.m_s[current-1] * theta_s)
            )
            current += 1
        return self.theta_list

    def psis(self) -> float:
        while len(self.psi_list) < self.inputLength-1:
            self.psi_list.append(
                self.psi_list[-1] + 180 - self.theta_list[len(self.psi_list)+1]
            )
        return self.psi_list

    def us(self) -> float:
        current = 0
        while len(self.u_list) < self.inputLength-1:
            self.u_list.append(
                self.u_list[-1] + d * math.cos(
                    math.radians(self.psi_list[current])
                )
            )
            current += 1
        return self.u_list
    
    def vs(self) -> float:
        current = 0
        while len(self.v_list) < self.inputLength-1:
            self.v_list.append(
                self.v_list[-1] + d * math.sin(
                    math.radians(self.psi_list[current])
                )
            )
            current += 1
        return self.v_list

    def cords(self) -> tuple:
        return tuple(zip(self.u_list, self.v_list))

generator = topView(m_c, m_s)
print(generator.cords())
# pen=None to hide pen
# ploted = pg.plot(u, v, title="Top View of DNA", symbol='o', symbolSize=80, pxMode=True)
# ploted.showGrid(x=True, y=True)
# app = QApplication(sys.argv)
# ploted.show()
# app.exec()