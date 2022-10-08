import math
from typing import List


class Plot:
    """
    Generate top view features.

    Attributes:
        theta_deltas (List[float]): List of all angle changes between domains.
        coords (dna_nanotube_tools.cords): Dna_nanotube_tools cords type object. Schema can be found in dna_nanotube_tools/types.coords.
        ui_widget (pyqtgraph.plot): Pyqtgraph widget to display the topview
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
        self.domain_count = len(domains)
        self.D = D
        self.computed = False  # has compute() been called?

        self._theta_c = theta_c
        self._theta_s = theta_s

    def compute(self):
        """
        Compute helices' top-view graph data
        """

        self.theta_deltas: List[float] = [0.0]  # list to store angle deltas in
        self.u_coords: List[float] = [0.0]  # list to store u cords in
        self.v_coords: List[float] = [0.0]  # list to store v cords in

        for domain_index in range(self.domain_count):
            # locate strand switch angle for the previous domain.
            theta_s: float = (
                self.domains[domain_index - 1].theta_switch_multiple * self._theta_s
            )
            # locate interior angle for the previous domain.
            interior_angle_multiple: float = (
                self.domains[domain_index - 1].theta_interior_multiple * self._theta_c
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

        self.computed = True
        return self

    def __repr__(self) -> str:
        round_to = 3
        match self.computed:
            case False:
                return "top_view(uncomputed top_view object)"
            case True:
                prettified_coords = list(
                    zip(
                        [round(coord, round_to) for coord in self.u_coords],
                        [round(coord, round_to) for coord in self.v_coords],
                    )
                )
                return f"top_view(coords={prettified_coords}, theta_deltas={[round(delta, round_to) for delta in self.theta_deltas]}"
            case _:
                return "top_view(uninitilized)"
