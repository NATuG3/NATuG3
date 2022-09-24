from functools import lru_cache
from types import FunctionType
from typing import Deque, Tuple, Type
from collections import deque
import pyqtgraph as pg
from dna_nanotube_tools.datatypes import domain, nucleoside, NEMid

# container to store data for domains in
DomainsContainer: FunctionType = lambda domain_count: tuple(
    (deque(), deque()) for i in range(domain_count)
)
# type annotation for the aforementioned container
DomainsContainerType: Type = Tuple[Tuple[Deque[float], Deque[float]], ...]


class side_view:
    """
    Generate data needed for a side view graph of helicies.
    """

    def __init__(
        self,
        domains: list,
        base_height: float,
        strand_switch_distance: float,
        strand_switch_angle: float,
        interpoint_angle_multiple=2,
        characteristic_angle=360 / 21,
    ) -> None:
        """
        Initilize side_view generation class.

        Args:
            domains (list): List of domains.
            base_height (float): Height between two bases (in Angstroms).
            strand_switch_distance (float): Strand switch distance (in Angstroms).
            strand_switch_angle (float): Angle about the helix axis between two nucleosides on different helices of a double helix.
            interpoint_angle_multiple (int, optional): Angle that one base makes about the helix axis, measured in multiples of characteristic angle.
            characteristic_angle (float, optional): Characteristic angle. Defaults to 360/21.

        Raises:
            ValueError: Length of interior_angles does not match that of strand_switch_angles.
        """

        self.domain_count = len(domains)
        self.domains = domains

        self.characteristic_angle = characteristic_angle
        self.strand_switch_angle = strand_switch_angle
        self.interpoint_angle = interpoint_angle_multiple * self.characteristic_angle
        self.base_height = base_height
        self.strand_switch_distance = strand_switch_distance

    def compute(self, count: int) -> DomainsContainerType:
        """
        Compute data for count# of points.

        Args:
            count (int): Number of points to compute data for.

        Returns:
            DomainsContainerType: A domains container of all points.
        """

        points = DomainsContainer(self.domain_count)
        for domain_index in range(self.domain_count):
            for strand_direction in range(2):
                for i in range(count):
                    # generate/retreive cached
                    angle = self._point_angles(count)[domain_index][strand_direction][i]
                    x_coord = self._x_coords(count)[domain_index][strand_direction][i]
                    z_coord = self._z_coords(count)[domain_index][strand_direction][i]

                    point = NEMid(x_coord, z_coord, angle, None)
                    points[domain_index][strand_direction].append(point)
        return points

    @lru_cache(maxsize=1)
    def _point_angles(self, count: int) -> DomainsContainerType:
        """Generate angles made about the central axis going counter-clockwise from the line of tangency."""
        point_angles = DomainsContainer(
            self.domain_count
        )  # container to store generated angles in

        # generate count# of point angles on a domain-by-domain basis
        # domain_index is the index of the current domain
        for domain_index in range(self.domain_count):
            # one strand direction will be initially set to zero
            # whereas the other will be set to zero - strand_switch_angle

            # set initial point angle values
            point_angles[domain_index][1].append(0.0)
            point_angles[domain_index][0].append(0.0 - self.strand_switch_angle)

            for i in range(count):

                # generate the next UP STRAND point angle
                # "point_angles[domain_index][0]" =
                # point angles -> current domain -> list of point angles for up strand -> previous one
                point_angles[domain_index][1].append(
                    point_angles[domain_index][1][i] + self.interpoint_angle
                )

                # generate the next DOWN STRAND point angle
                # "point_angles[domain_index][0][i+1]" =
                # point angles -> current domain -> list of point angles for up strand -> one we just computed
                point_angles[domain_index][0].append(
                    point_angles[domain_index][1][i + 1] - self.strand_switch_angle
                )

        return point_angles

    @lru_cache(maxsize=1)
    def _x_coords(self, count: int) -> DomainsContainerType:
        """Generate x cords."""
        x_coords: DomainsContainerType = DomainsContainer(
            self.domain_count
        )  # container to store generated x coords in
        point_angles: DomainsContainerType = self._point_angles(
            count
        )  # point angles are needed to generate x coords

        # generate count# of x coords on a domain-by-domain basis
        # domain_index is the index of the current domain
        for domain_index in range(self.domain_count):
            # current exterior and interior angles
            # note that "exterior_angle == 360 - interior_angle"
            theta_interior: float = (
                self.domains[domain_index].theta_interior_multiple
                * self.characteristic_angle
            )
            exterior_angle: float = 360 - theta_interior

            for i in range(count):
                for strand_direction in range(
                    2
                ):  # repeat same steps for up and down strand
                    # find the current point_angle and modulo it by 360
                    # point angles are "the angle about the central axis going counter-clockwise from the line of tangency."
                    # they reset at 360, so we modulo the current point angle here
                    point_angle: float = (
                        point_angles[domain_index][strand_direction][i] % 360
                    )

                    if point_angle < exterior_angle:
                        x_coord = point_angle / exterior_angle
                    else:
                        x_coord = (360 - point_angle) / theta_interior

                    # domain 0 lies between [0, 1] on the x axis
                    # domain 1 lies between [1, 2] on the x axis
                    # ext...
                    x_coord += domain_index

                    # store the new x_coord in the container object and continue
                    x_coords[domain_index][strand_direction].append(x_coord)

        return x_coords

    @lru_cache(maxsize=1)
    def _z_coords(self, count: int, NEMid=True) -> DomainsContainerType:
        """Generate z cords."""
        # if there are multiple domains ensure "count" is over 21, because we would not be able to get a full
        # sample of the x coords for finding the best places to place bases
        if self.domain_count > 0:
            if count < 21:
                raise Exception(
                    "Not enough domains. Count must be > 21 when multiple domains are passed."
                )

        # since all initial z_coord values are pre-set we reduce the count (which is used for itterating) by 1
        count -= 1

        # create container for all the z coords for each domain
        # each z cord is in the form [(<up_strand>, <down_strand>), ...]
        # tuple index is which domain it represents, and <up_strand> & <down_strand> are arrays of actual z coords
        z_coords: DomainsContainerType = DomainsContainer(self.domain_count)

        # arbitrarily define the z_coord of the up strand of domain#0 to be 0
        z_coords[0][0].append(0.0)
        z_coords[0][1].append(0.0 - self.strand_switch_distance)

        # we cannot calcuate the z_coords for domains after the first one unless we find the z_coords for the first one first
        # the first domain has its initial z cords (up and down strands) set to (arbitrary) static values, whereas other domains do not
        # for all domains except domain#0 the initial z cord will rely on a specific z cord of the previous
        # and so, we calculate the z coords of domain#0...
        for i in range(count):
            # generate the next z_coord for the down strand...
            # "z_coords[0][0][i] " means "z_coords -> domain#0 -> up_strand -> previous z_coord"
            z_coords[0][0].append(z_coords[0][0][i] + self.base_height)

            # generate the next z_coord for the up strand...
            # "z_coords[0][1][i+1]" means "z_coords -> domain#0 -> up_strand -> z_coord we just computed
            z_coords[0][1].append(z_coords[0][0][i + 1] - self.strand_switch_distance)

        # now find and append the initial z_coord for each domain
        for domain_index in range(1, self.domain_count):
            previous_domain_index: int = domain_index - 1  # the previous domain's index

            # step 1: find the initial z cord for the current domain_index

            # lets find the maxmimum x cord for the previous domain
            # that will be the point where, when placed adjacently to the right in the proper place
            # there will be an overlap of bases
            initial_z_coord: DomainsContainerType = self._x_coords(count)[
                previous_domain_index
            ][0]
            # initial_z_coord = previous domains's up strand's rightmost x coord

            initial_z_coord: int = initial_z_coord.index(max(initial_z_coord))
            # obtain the index of the rightmost x coord on the strand

            # we are going to line up the next up strand so that its leftmost (first) point touches the previous domain's rightmost
            initial_z_coord: float = z_coords[previous_domain_index][0][initial_z_coord]

            # append this new initial z cord to the actual list of z_coords
            z_coords[domain_index][1].append(initial_z_coord)
            z_coords[domain_index][0].append(
                initial_z_coord - self.strand_switch_distance
            )

            # step 2: actually calculate the z coords of this new domain

            for i in range(count):  # (domain 0 is already calculated)
                # append the previous z_coord + the base_height
                # "z_coords[i][0][i]" == "z_coords -> domain#i -> up_strand -> previous one"
                z_coords[domain_index][1].append(
                    z_coords[domain_index][1][i] + self.base_height
                )

                # append the previous z_coord's up strand value, minus the strand switch distance
                # "z_coords[i][0][i]" == "z_coords -> domain#i -> down_strand -> z_coord we just calculated"
                z_coords[domain_index][0].append(
                    z_coords[domain_index][1][i + 1] - self.strand_switch_distance
                )

        return z_coords

    def ui(self, count: int) -> pg.GraphicsLayoutWidget:
        """
        Generate PyQt widget for side view.

        Args:
            count (int): Number of points to generate per domain.
        """
        plotted_window: pg.GraphicsLayoutWidget = (
            pg.GraphicsLayoutWidget()
        )  # create main plotting window
        plotted_window.setWindowTitle("Side View of DNA")  # set the window's title
        plotted_window.setBackground("w")  # make the background white
        main_plot: pg.plot = plotted_window.addPlot()

        # we can calculate the range at the end of generation; we don't need to continiously recalculate the range
        main_plot.disableAutoRange()

        # generate the coords
        x_coords = self._x_coords(count)
        z_coords = self._z_coords(count)

        for domain_index in range(self.domain_count):
            if domain_index % 2:  # if the domain index is an even integer
                colors: tuple = ((255, 0, 0), (0, 255, 0))  # use red and green colors
            else:  # but if it is an odd integer
                colors: tuple = ((0, 0, 255), (255, 255, 0))  # use blue and yellow colors
            # this way it will be easy to discern between different domains
            # (every other domain will be a different color scheme)

            for strand_direction in range(2):
                if strand_direction == 0:  # 0 means up strand
                    symbol: str = "t1"  # up arrow for up strand
                    color: str = colors[
                        0
                    ]  # set the color to be the second option of current color scheme (which is "colors")
                elif strand_direction == 1:  # 1 means down strand
                    symbol: str = "t"  # down arrow for down strand
                    color: str = colors[
                        1
                    ]  # set the color to be the first option of current color scheme (which is "colors")

                # domain#i-up or domain#i-down
                title = f"domain#{domain_index}-{str(strand_direction).replace('0','up').replace('1','down')}"

                main_plot.plot(  # actually plot the current strand of the current domain
                    x_coords[domain_index][strand_direction],
                    z_coords[domain_index][strand_direction],
                    title=title,  # name of what was just plotted
                    symbol=symbol,  # type of symbol (in this case up/down arrow)
                    symbolSize=6,  # size of arrows in px
                    pxMode=True,  # means that symbol size is in px
                    symbolPen=pg.mkPen(
                        color=color
                    ),  # set color of points to current color
                    pen=pg.mkPen(
                        color=(120, 120, 120), width=1.8
                    ) # set color of pen to current color (but darker)
                )

        main_plot.setAspectLocked(lock=True, ratio=116)
        main_plot.autoRange()  # reenable autorange so that it isn't zoomed out weirdly

        return plotted_window
