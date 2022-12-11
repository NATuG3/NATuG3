import logging
import math
from typing import List

logger = logging.getLogger(__name__)


class TopViewWorker:
    """
    Top view plotter.

    Attributes:
        domains: All inputted workers.
        nucleic_acid_profile: The nucleic acid profile used for top view computations.
        u_coords: All u coords.
        v_coords: All v coords.
        angle_deltas: All angle changes from NEMid-to-NEMid
    """

    def __init__(self, domains: "Domains") -> None:
        """
        Initialize a TopViewWorker object.

        Args:
            domains: The domains to generate a top view for.
        """
        self.domains = domains
        self.nucleic_acid_profile = domains.nucleic_acid_profile

        self.theta_deltas: List[float] = [0.0]  # list to store angle deltas in
        self.u_coords: List[float] = [0.0]  # list to store u cords in
        self.v_coords: List[float] = [0.0]  # list to store v cords in

        self.compute()

    def compute(self) -> None:
        """Compute u_coords, v_coords, and angle_deltas."""
        for index, domain in enumerate(self.domains.domains()):
            # locate strand switch angle for the previous domain.
            theta_s: float = (
                self.domains.domains()[index - 1].theta_s_multiple
                * self.nucleic_acid_profile.theta_s
            )
            # locate interior angle for the previous domain.
            interior_angle_multiple: float = (
                self.domains.domains()[index - 1].theta_interior_multiple
                * self.nucleic_acid_profile.theta_c
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
            self.u_coords.append(
                self.u_coords[-1] + self.nucleic_acid_profile.D * math.cos(angle_delta)
            )

            # append the v cord of the domain to "self.v_coords"
            self.v_coords.append(
                self.v_coords[-1] + self.nucleic_acid_profile.D * math.sin(angle_delta)
            )

        logger.debug("Performed top view computation.")

    def __repr__(self) -> str:
        """Return a string representation of the TopViewWorker object."""
        round_to = 3
        prettified_coords = list(
            zip(
                [round(coord, round_to) for coord in self.u_coords],
                [round(coord, round_to) for coord in self.v_coords],
            )
        )
        return (
            f"TopViewWorker("
            f"coords={prettified_coords}, "
            f"theta_deltas={[round(delta, round_to) for delta in self.theta_deltas]}"
            f") "
        )
