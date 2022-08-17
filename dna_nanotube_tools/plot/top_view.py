import math
import pyqtgraph as pg
import dna_nanotube_tools


class top_view:
    """
    Generate top view features.

    Attributes:
        self.domains (List[dna_nanotube_tools.domain]): List of all domains inputted.
        angle_deltas (List[float]) = List of all angle changes between domains.
        coords (dna_nanotube_tools.cords) = Dna_nanotube_tools cords type object. Schema can be found in dna_nanotube_tools/types.coords.
        ui_widget (pyqtgraph.plot): Pyqtgraph widget to display the topview
    """

    def __init__(
        self,
        domains: list,
        domain_distance: float,
        characteristic_angle=360 / 21,
        strand_switch_angle=2.3,
    ):
        """
        Generate (u, v) cords for top view of helices generation.

        Args:
            domains (List[dna_nanotube_tools]): List of domains.
            domain_distance (float): Distance between any given two domain centers.
            characteristic_angle (float, optional): Characteristic angle.
            strand_switch_angle (float, optional): Strand switch angle.
        """

        domain_count = len(domains)  # number of domains
        angle_deltas = [0]  # create list to store angle changes in
        us = [0]  # create list to store u cords in
        vs = [0]  # create list to store v cords in

        for counter in range(domain_count):
            # locate strand switch angle for (counter - 1)'s domain. (the previous domain)
            strand_switch_angle = (
                domains[counter - 1].switch_angle_multiple * strand_switch_angle
            )
            # locate interior angle for (counter - 1)'s domain. (the previous domain)
            interjunction_angle = (
                domains[counter - 1].interjunction_multiple * characteristic_angle
            )
            # calculate the actual interior angle (with strand switching angle factored in)
            interior_angle = interjunction_angle - strand_switch_angle

            # append the angle change to "angle_deltas"
            angle_deltas.append(angle_deltas[-1] + 180 - interior_angle)
            # (current angle delta) AKA most previously appended angle delta
            angle_delta = angle_deltas[-1]

            # append the u cord of the domain to "us"
            us.append(us[-1] + domain_distance * math.cos(math.radians(angle_delta)))

            # append the v cord of the domain to "vs"
            vs.append(vs[-1] + domain_distance * math.sin(math.radians(angle_delta)))

        # create PyQtGraph widget
        ui_widget = pg.plot(
            us,
            vs,
            title="Top View of DNA",
            symbol="o",
            symbolSize=80,
            pxMode=True,
        )
        ui_widget.setAspectLocked(lock=True, ratio=1)
        ui_widget.showGrid(x=True, y=True)

        # convert calculated coords into actual coords object
        coords = dna_nanotube_tools.coords()
        coords.xs = us
        coords.ys = vs

        # store main outputs in class
        self.domains = domains
        self.angle_deltas = angle_deltas
        self.coords = coords
        self.ui_widget = ui_widget
