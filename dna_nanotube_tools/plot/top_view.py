import math
from typing import Tuple, List


class top_view:
    """
    Generate (u, v) cords for top view of helices generation.

    Attributes:
        interior_angles (list): List of interior angles per domain transition.
        strand_switch_angles (list): List of strand switch angles per domain transition.
        domain_distance (float): Distance between any given two domain centers.
        characteristic_angle (float, optional): Characteristic angle.
        strand_switch_angle (float, optional): Strand switch angle.
    """

    def __init__(
        self,
        interior_angle_multiples: List[int],
        strand_switch_angle_multiples: List[int],
        domain_distance: float,
        characteristic_angle=360 / 21,
        strand_switch_angle=0,
    ) -> None:
        """
        Initilize top_view generation class.

        Args:
            interior_angle_multiples (List[int]): List of interior angles per domain transition. List of multiples of characteristic angle.
            strand_switch_angle_multiples (List[int]): List of strand switch angles per domain transition. List of multiples of strand switch angle.
            domain_distance (float): Distance between any given two domain centers.
            characteristic_angle (float, optional): Characteristic angle. Defaults to 360/21.
            strand_switch_angle (float, optional): strand switch angle. Defaults to 0.
        Raises:
            ValueError: Length of strand_switch_angle_multiples does not match that of strand switch angles.
        """
        if len(interior_angle_multiples) != len(strand_switch_angle_multiples):
            raise ValueError(
                "Length of strand_switch_angle_multiples does not match that of strand_switch_angle_multiples"
            )

        self.characteristic_angle = characteristic_angle
        self.strand_switch_angle = strand_switch_angle
        self.domain_distance = domain_distance

        self.input_length = len(interior_angle_multiples)

        self.strand_switch_angles = [
            angle * self.strand_switch_angle for angle in strand_switch_angle_multiples
        ]

        # Note that "_cache" is appended to variables used by functions. Do not use these attributes directly; instead call related function.
        self.angle_delta_cache = [0]  # related function: angle_deltas()
        self.interior_angle_cache = [  # related function: interior_angles()
            angle * self.characteristic_angle for angle in interior_angle_multiples
        ]
        self.u_cache = [0]  # related function: us()
        self.v_cache = [0]  # related function vs()

    def interior_angle_by_index(self, index: int) -> float:
        """
        Obtain a interior_angle (interior angle) given a specific index.

        Args:
            index (int): Index of interior_angle to return.
        Returns:
            float: Requested interior angle's value.
        """
        return self.interior_angles[index - 1] - (self.strand_switch_angles[index - 1])

    def interior_angles(self) -> List[float]:
        """
        Generate list of interior angles ("interior_angles") or return existing list.

        Returns:
            list: list of all interior_angles.
        """
        current = 0
        while len(self.interior_angle_cache) < self.input_length:
            self.interior_angle_cache.append(
                (self.interior_angles[current - 1])
                - (self.strand_switch_angles[current - 1])
            )
            current += 1
        return self.interior_angle_cache

    def angle_deltas(self) -> list:
        """
        Generate list of angle changes ("angle_deltas") or return existing list.

        Returns:
            list: list of all angle_deltas.
        """
        current = 0
        
        while len(self.angle_delta_cache) < self.input_length:
            self.angle_delta_cache.append(
                self.angle_delta_cache[-1] + 180 - self.interior_angle_cache[current]
            )
            current += 1

        return self.angle_delta_cache

    def us(self) -> list:
        """
        Generate a list of horizontal cords ("u cords").
        Returns:
            list: list of all u cords.
        """
        current = 0

        while len(self.u_cache) <= self.input_length:
            self.u_cache.append(
                self.u_cache[-1]
                + self.domain_distance
                * math.cos(math.radians(self.angle_deltas()[current]))
            )
            current += 1
            
        return self.u_cache

    def vs(self) -> list:
        """
        Generate a list of vertical cords ("v cords").
        Returns:
            list: list of all v cords.
        """
        current = 0

        while len(self.v_cache) <= self.input_length:
            self.v_cache.append(
                self.v_cache[-1]
                + self.domain_distance
                * math.sin(math.radians(self.angle_deltas()[current]))
            )
            current += 1

        return self.v_cache

    def cords(self) -> Tuple[Tuple[float, float], ...]:
        """
        Obtain list of all cords.

        Returns:
            Tuple[Tuple[float, float], ...]: tuple of tuples of all (u, v) cords.
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
