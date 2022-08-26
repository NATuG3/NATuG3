import math
from typing import List
import pyqtgraph as pg


class top_view:
    """
    Generate top view features.

    Attributes:
        angle_deltas (List[float]): List of all angle changes between domains.
        coords (dna_nanotube_tools.cords): Dna_nanotube_tools cords type object. Schema can be found in dna_nanotube_tools/types.coords.
        ui_widget (pyqtgraph.plot): Pyqtgraph widget to display the topview
    """

    def __init__(
        self,
        domains: list,
        domain_distance: float,
        characteristic_angle=360 / 21,
        strand_switch_angle=2.3,
    ) -> None:
        """
        Generate (u, v) cords for top view of helices generation.

        Args:
            domains (List[dna_nanotube_tools]): List of domains.
            domain_distance (float): Distance between any given two domain centers.
            characteristic_angle (float, optional): Characteristic angle.
            strand_switch_angle (float, optional): Strand switch angle.
        """
        domain_count = len(domains)  # number of domains inputted
        self.angle_deltas: List[float] = [0.0]  # list to store angle deltas in
        self.u_coords: List[float] = [0.0]  # list to store u cords in
        self.v_coords: List[float] = [0.0]  # list to store v cords in

        for counter in range(domain_count):
            # locate strand switch angle for the previous domain.
            strand_switch_angle: float = (
                domains[counter - 1].switch_angle_multiple * strand_switch_angle
            )
            # locate interior angle for the previous domain.
            interjunction_angle: float = (
                domains[counter - 1].interjunction_multiple * characteristic_angle
            )

            # calculate the actual interior angle (with strand switching angle factored in)
            interior_angle: float = interjunction_angle - strand_switch_angle

            # append the angle change to "self.angle_deltas"
            self.angle_deltas.append(self.angle_deltas[-1] + 180 - interior_angle)

            # the current angle delta (we will use it to generate the next one)
            angle_delta: float = self.angle_deltas[-1]
            angle_delta: float = math.radians(
                angle_delta
            )  # convert to radians (AKA angle_delta*(180/pi))

            # append the u cord of the domain to "self.u_coords"
            self.u_coords.append(
                self.u_coords[-1] + domain_distance * math.cos(angle_delta)
            )

            # append the v cord of the domain to "self.v_coords"
            self.v_coords.append(
                self.v_coords[-1] + domain_distance * math.sin(angle_delta)
            )

    def ui(self) -> pg.GraphicsLayoutWidget:
        """
        Generate PyQt widget for top view.
        """
        plotted_window: pg.GraphicsLayoutWidget = (
            pg.GraphicsLayoutWidget()
        )  # create main plotting window
        plotted_window.setWindowTitle("Top View of DNA")  # set the window's title
        plotted_window.setBackground("w")  # make the background white

        main_plot = plotted_window.addPlot()

        main_plot.plot(
            self.u_coords,
            self.v_coords,
            title="Top View of DNA",
            symbol="o",
            symbolSize=80,
            pxMode=True,
        )

        return plotted_window
