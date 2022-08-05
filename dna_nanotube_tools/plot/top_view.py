import math
from typing import Tuple


class top_view:
    """
    Generate (u, v) cords for top view of helices generation.

    Attributes:
        interior_angles (int): Interior angle, measured as a multiple of the characteristic angle.
        switch_angles (int): List of switch angle multiples.
        d (float): Distance between helicies.
        theta_c (float): Characteristic angle.
        theta_s (float): Switch angle.
    """

    def __init__(
        self,
        interior_angles: list,
        switch_angles: list,
        d: float,
        theta_c=360 / 21,
        theta_s=0,
    ) -> None:
        """
        Initilize top_view generation class.

        Args:
            interior_angles (list): List of multiples of characteristic angle.
            switch_angles (list): List of multiples of switch angle.
            d (float): Distance between helicies.
            theta_c (float, optional): Characteristic angle. Defaults to 360/21.
            theta_s (float, optional): Switch angle. Defaults to 0.
        Raises:
            ValueError: Length of interior_angles does not match that of switch_angles.
        """
        if len(interior_angles) != len(switch_angles):
            raise ValueError("len(interior_angles) != len(switch_angles)")

        self.theta_c = theta_c
        self.theta_s = theta_s
        self.d = d

        self.input_length = len(interior_angles)

        self.interior_angles = [angle * self.theta_c for angle in interior_angles]
        self.switch_angles = switch_angles

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
        return self.interior_angles[index - 1] - (
            self.switch_angles[index - 1] * self.theta_s
        )

    def thetas(self) -> list:
        """
        Generate list of interior angles ("thetas") or return existing list.
        Returns:
            list: list of all thetas.
        """
        current = 0
        while len(self.theta_list) < self.input_length:
            self.theta_list.append(
                (self.interior_angles[current - 1])
                - (self.switch_angles[current - 1] * self.theta_s)
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
        while len(self.psi_list) < self.input_length:
            self.psi_list.append(self.psi_list[-1] + 180 - self.theta_list[current])
            current += 1
        return self.psi_list

    def us(self) -> list:
        """
        Generate a list of horizontal cords ("u cords").
        Returns:
            list: list of all u cords.
        """
        current = 0
        while len(self.u_list) <= self.input_length:
            self.u_list.append(
                self.u_list[-1]
                + self.d * math.cos(math.radians(self.psi_list[current]))
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
        while len(self.v_list) <= self.input_length:
            self.v_list.append(
                self.v_list[-1]
                + self.d * math.sin(math.radians(self.psi_list[current]))
            )
            current += 1
        return self.v_list

    def cords(self) -> Tuple[Tuple[float, float]]:
        """
        Obtain list of all cords.
        Returns:
            Tuple[float, float]: tuple of tuples of all (u, v) cords.
        """
        return tuple(zip(self.us(), self.vs()))

    def ui(self):
        """
        Return PyQt widget of topview.
        Returns:
            pg.plot: PyQt widget of topview.
        """
        import pyqtgraph as pg

        ui = pg.plot(
            self.us(),
            self.vs(),
            title="Top View of DNA",
            symbol="o",
            symbolSize=80,
            pxMode=True,
        )
        ui.setAspectLocked(lock=True, ratio=1)
        ui.showGrid(x=True, y=True)
        return ui
