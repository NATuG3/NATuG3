import math
from typing import Tuple

class top_view():
    """
    Generate (u, v) cords for topview of helices generation.

    Attributes:
        m_c: list of characteristic angle multiples.
        m_s: list of switch angle multiples.
    """

    def __init__(self, m_c: list, m_s: list, d: float, theta_c = 360/21, theta_s = 0) -> None:
        """
        Initilize topview generation class.

        Args:
            m_c (list): list of multiples of characteristic angle.
            m_s (list): list of multiples of switch angle.
            d (float): distance between helicies
            theta_c (float, optional): Characteristic angle. Defaults to 360/21.
            theta_s (float, optional): Switch angle. Defaults to 0.

        Raises:
            ValueError: Length of m_c does not that of m_s.
        """
        if len(m_c) != len(m_s):
            raise ValueError("len(m_c) != len(m_s)")

        self.theta_c = theta_c
        self.theta_s = theta_s
        self.d = d

        self.inputLength = len(m_c)

        self.m_c = m_c
        self.m_s = m_s

        self.psi_list = [0]
        self.theta_list = []

        self.u_list = [0]
        self.v_list = [0]

        self.thetas()
        self.psis()

    def theta_by_index(self, index: int) -> float:
        """
        Obtain a theta (interior angle) given a specific index.

        Args:
            index (int): index of theta to return.

        Returns:
            float: theta's value.
        """
        return (self.m_c[index-1] * self.theta_c) - (self.m_s[index-1] * self.theta_s)

    def thetas(self) -> list:
        """
        Generate list of interior angles ("thetas") or return existing list.

        Returns:
            list: list of all thetas.
        """
        current = 0
        while len(self.theta_list) < self.inputLength:
            self.theta_list.append(
                (self.m_c[current-1] * self.theta_c) - (self.m_s[current-1] * self.theta_s)
            )
            current += 1
        return self.theta_list

    def psis(self) -> list:
        """
        Generate list of angle changes ("psis") or return existing list.

        Returns:
            list: list of all psis.
        """
        current = 0
        while len(self.psi_list) < self.inputLength:
            self.psi_list.append(
                self.psi_list[-1] + 180 - self.theta_list[current]
            )
            current += 1
        return self.psi_list

    def us(self) -> list:
        """
        Generate a list of horizontal cords ("u cords").

        Returns:
            list: list of all u cords.
        """
        current = 0
        while len(self.u_list) < self.inputLength:
            self.u_list.append(
                self.u_list[-1] + self.d * math.cos(
                    math.radians(self.psi_list[current])
                )
            )
            current += 1
        return self.u_list
    
    def vs(self) -> list:
        """
        Generate a list of vertical cords ("v cords").

        Returns:
            list: list of all v cords.
        """
        current = 0
        while len(self.v_list) < self.inputLength:
            self.v_list.append(
                self.v_list[-1] + self.d * math.sin(
                    math.radians(self.psi_list[current])
                )
            )
            current += 1
        return self.v_list

    def cords(self) -> Tuple[float, float]:
        """
        Obtain list of all cords.

        Returns:
            Tuple[float, float]: tuple of tuples of all (u, v) cords.
        """
        return tuple(
            zip(
                self.us(), self.vs()
                )
            )

    def ui(self):
        """
        Return PyQt widget of topview.

        Returns:
            pg.plot: PyQt widget of topview.
        """
        import pyqtgraph as pg
        ui = pg.plot(
                self.us(), self.vs(), title="Top View of DNA", symbol='o', symbolSize=80, pxMode=True
                )
        ui.setAspectLocked(lock=True, ratio=1)
        ui.showGrid(x=True, y=True)
        return ui