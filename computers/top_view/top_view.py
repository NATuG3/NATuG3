import math
from typing import List

from computers.top_view.interface import Plotter


class TopView:
    """
    Top view plotter.

    Attributes:
        domains (List[Domain]): All inputted domains.
        u_coords (List[float]): All u coords.
        v_coords (List[float]): All v coords.
        angle_deltas (List[float]): All angle angle changes from NEMid-to-NEMid
    """

    def __init__(
        self,
        domains: list,
        D: float,
        theta_c=360 / 21,
        theta_s=2.3,
    ) -> None:
        """
        Generate (u, v) cords for top view of helices generation.

        Args:
            domains (List[dna_nanotube_tools]): List of domains.
            D (float): Distance between any given two domain centers (nanometers).
            theta_c (float, optional): Characteristic angle.
            theta_s (float, optional): Strand switch angle.
        """
        self.domains = domains
        self.D = D

        self.theta_c = theta_c
        self.theta_s = theta_s

        self.theta_deltas: List[float] = [0.0]  # list to store angle deltas in
        self.u_coords: List[float] = [0.0]  # list to store u cords in
        self.v_coords: List[float] = [0.0]  # list to store v cords in
        self.compute()

    def compute(self):
        """Compute u_coords, v_coords, and angle_deltas."""
        for index, domain in enumerate(self.domains):
            # locate strand switch angle for the previous domain.
            theta_s: float = (
                self.domains[index - 1].theta_switch_multiple * self.theta_s
            )
            # locate interior angle for the previous domain.
            interior_angle_multiple: float = (
                self.domains[index - 1].theta_interior_multiple * self.theta_c
            )

            # calculate the actual interior angle (with strand switching angle factored in)
            interior_angle: float = interior_angle_multiple - theta_s

            # append the angle change to "self.angle_deltas"
            self.theta_deltas.append(self.theta_deltas[-1] + 180 - interior_angle)

            # the current angle delta (we will use it to generate the next one)
            angle_delta: float = self.theta_deltas[-1]
            angle_delta: float = math.radians(
                angle_delta
            )  # convert to radians (AKA angle_delta*(180/pi))

            # append the u cord of the domain to "self.u_coords"
            self.u_coords.append(self.u_coords[-1] + self.D * math.cos(angle_delta))

            # append the v cord of the domain to "self.v_coords"
            self.v_coords.append(self.v_coords[-1] + self.D * math.sin(angle_delta))

    def ui(self):
        return Plotter(self)

    def __repr__(self) -> str:
        round_to = 3
        prettified_coords = list(
            zip(
                [round(coord, round_to) for coord in self.u_coords],
                [round(coord, round_to) for coord in self.v_coords],
            )
        )
        return f"top_view(coords={prettified_coords}, theta_deltas={[round(delta, round_to) for delta in self.theta_deltas]} "
