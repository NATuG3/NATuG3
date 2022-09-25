from functools import lru_cache
from types import FunctionType
from typing import Deque, Tuple, Type
from collections import deque
import pyqtgraph as pg
from dna_nanotube_tools.datatypes import domain, nucleoside, NEMid

# container to store data for domains in
DomainsContainer: FunctionType = lambda domain_count: tuple(
    (deque(), deque()) for _ in range(domain_count)
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
        Z_b: float,
        Z_s: float,
        theta_s: float,
        theta_b: float,
        theta_c: float,
    ) -> None:
        """
        Initilize side_view generation class.

        Args:
            domains (list): List of domains.
            Z_b (float): Base height (in nm)
            Z_s (float): Strand switch distance (in nm).
            theta_s (float): Switch angle (in degrees).
            theta_b (float): Base angle (in degrees).
            theta_c (float): Characteristic angle (in degrees).

        Raises:
            ValueError: Length of interior_angles does not match that of theta_ss.
        """

        self.domain_count = len(domains)
        self.domains = domains

        self.Z_b = Z_b
        self.Z_s = Z_s

        self.theta_s = theta_s
        self.theta_b = theta_b
        self.theta_c = theta_c

    def compute(self, count: int) -> DomainsContainerType:
        """
        Compute data for count# of NEMids.

        Args:
            count (int): Number of NEMids to compute data for.

        Returns:
            DomainsContainerType: A domains container of all NEMids.
        """

        NEMids = DomainsContainer(self.domain_count)
        for domain_index in range(self.domain_count):
            for strand_direction in range(2):
                for i in range(count):
                    # generate/retreive cached
                    angle = self._NEMid_angles(count)[domain_index][strand_direction][i]
                    x_coord = self._x_coords(count)[domain_index][strand_direction][i]
                    z_coord = self._z_coords(count)[domain_index][strand_direction][i]

                    NEMid = NEMid(x_coord, z_coord, angle, None)
                    NEMids[domain_index][strand_direction].append(NEMid)
        return NEMids

    @lru_cache(maxsize=1)
    def _NEMid_angles(self, count: int) -> DomainsContainerType:
        """Generate angles made about the central axis going counter-clockwise from the line of tangency for count# of NEMids."""
        NEMid_angles = DomainsContainer(
            self.domain_count
        )  # container to store generated angles in

        # generate count# of NEMid angles on a domain-by-domain basis
        # domain_index is the index of the current domain
        for domain_index in range(self.domain_count):
            # one strand direction will be initially set to zero
            # whereas the other will be set to zero - theta_s

            # set initial NEMid angle values
            NEMid_angles[domain_index][1].append(0.0)
            NEMid_angles[domain_index][0].append(0.0 - self.theta_s)

            for i in range(count):

                # generate the next UP STRAND NEMid angle
                # "NEMid_angles[domain_index][0]" =
                # NEMid angles -> current domain -> list of NEMid angles for up strand -> previous one
                NEMid_angles[domain_index][1].append(
                    NEMid_angles[domain_index][1][i] + self.theta_b
                )

                # generate the next DOWN STRAND NEMid angle
                # "NEMid_angles[domain_index][0][i+1]" =
                # NEMid angles -> current domain -> list of NEMid angles for up strand -> one we just computed
                NEMid_angles[domain_index][0].append(
                    NEMid_angles[domain_index][1][i + 1] - self.theta_s
                )

        return NEMid_angles

    @lru_cache(maxsize=1)
    def _x_coords(self, count: int) -> DomainsContainerType:
        """Generate count# of x cords."""
        x_coords: DomainsContainerType = DomainsContainer(
            self.domain_count
        )  # container to store generated x coords in
        NEMid_angles: DomainsContainerType = self._NEMid_angles(
            count
        )  # NEMid angles are needed to generate x coords

        # generate count# of x coords on a domain-by-domain basis
        # domain_index is the index of the current domain
        for domain_index in range(self.domain_count):
            # current exterior and interior angles
            # note that "theta_exterior == 360 - interior_angle"
            theta_interior: float = (
                self.domains[domain_index].theta_interior_multiple * self.theta_c
            )
            theta_exterior: float = 360 - theta_interior

            for i in range(count):
                for strand_direction in range(
                    2
                ):  # repeat same steps for up and down strand
                    # find the current NEMid_angle and modulo it by 360
                    # NEMid angles are "the angle about the central axis going counter-clockwise from the line of tangency."
                    # they reset at 360, so we modulo the current NEMid angle here
                    NEMid_angle: float = (
                        NEMid_angles[domain_index][strand_direction][i] % 360
                    )

                    if NEMid_angle < theta_exterior:
                        x_coord = NEMid_angle / theta_exterior
                    else:
                        x_coord = (360 - NEMid_angle) / theta_interior

                    # domain 0 lies between [0, 1] on the x axis
                    # domain 1 lies between [1, 2] on the x axis
                    # ext...
                    x_coord += domain_index

                    # store the new x_coord in the container object and continue
                    x_coords[domain_index][strand_direction].append(x_coord)

        return x_coords

    @lru_cache(maxsize=1)
    def _z_coords(self, count: int) -> DomainsContainerType:
        """Generate count# of z cords."""
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
        z_coords[0][1].append(0.0 - self.Z_s)

        # we cannot calcuate the z_coords for domains after the first one unless we find the z_coords for the first one first
        # the first domain has its initial z cords (up and down strands) set to (arbitrary) static values, whereas other domains do not
        # for all domains except domain#0 the initial z cord will rely on a specific z cord of the previous
        # and so, we calculate the z coords of domain#0...
        for i in range(count):
            # generate the next z_coord for the down strand...
            # "z_coords[0][0][i] " means "z_coords -> domain#0 -> up_strand -> previous z_coord"
            z_coords[0][0].append(z_coords[0][0][i] + self.Z_b)

            # generate the next z_coord for the up strand...
            # "z_coords[0][1][i+1]" means "z_coords -> domain#0 -> up_strand -> z_coord we just computed
            z_coords[0][1].append(z_coords[0][0][i + 1] - self.Z_s)

        # now find and append the initial z_coord for each domain
        for domain_index in range(1, self.domain_count):
            previous_domain_index: int = domain_index - 1  # the previous domain's index

            # step 1: find the initial z cord for the current domain_index

            # lets find the maxmimum x cord for the previous domain
            # that will be the NEMid where, when placed adjacently to the right in the proper place
            # there will be an overlap of bases
            initial_z_coord: DomainsContainerType = self._x_coords(count)[
                previous_domain_index
            ][0]
            # initial_z_coord = previous domains's up strand's rightmost x coord

            initial_z_coord: int = initial_z_coord.index(max(initial_z_coord))
            # obtain the index of the rightmost x coord on the strand

            # we are going to line up the next up strand so that its leftmost (first) NEMid touches the previous domain's rightmost
            initial_z_coord: float = z_coords[previous_domain_index][0][initial_z_coord]

            # append this new initial z cord to the actual list of z_coords
            z_coords[domain_index][1].append(initial_z_coord)
            z_coords[domain_index][0].append(initial_z_coord - self.Z_s)

            # step 2: actually calculate the z coords of this new domain

            for i in range(count):  # (domain 0 is already calculated)
                # append the previous z_coord + the Z_b
                # "z_coords[i][0][i]" == "z_coords -> domain#i -> up_strand -> previous one"
                z_coords[domain_index][1].append(
                    z_coords[domain_index][1][i] + self.Z_b
                )

                # append the previous z_coord's up strand value, minus the strand switch distance
                # "z_coords[i][0][i]" == "z_coords -> domain#i -> down_strand -> z_coord we just calculated"
                z_coords[domain_index][0].append(
                    z_coords[domain_index][1][i + 1] - self.Z_s
                )

        return z_coords

    def ui(self, count: int) -> pg.GraphicsLayoutWidget:
        """
        Generate PyQt widget for side view.

        Args:
            count (int): Number of NEMids to generate per domain.
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
                colors: tuple = (
                    (0, 0, 255),
                    (255, 255, 0),
                )  # use blue and yellow colors
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
                    ),  # set color of NEMids to current color
                    pen=pg.mkPen(
                        color=(120, 120, 120), width=1.8
                    ),  # set color of pen to current color (but darker)
                )

        main_plot.setAspectLocked(lock=True, ratio=116)
        main_plot.autoRange()  # reenable autorange so that it isn't zoomed out weirdly

        return plotted_window
