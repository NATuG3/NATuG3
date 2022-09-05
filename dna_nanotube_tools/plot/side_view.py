from typing import List, Tuple, NamedTuple
from collections import namedtuple
from dna_nanotube_tools.helpers import exec_on_innermost
import pyqtgraph as pg
from functools import cache

# datatype to store strand data in
# (this is a function that returns a template whenever called)
StrandsContainer = lambda: namedtuple("StrandData", "up_strand down_strand")(
    list(), list()
)
# the actual type (for type annotations)
StrandsContainerType: NamedTuple = NamedTuple(
    "StrandData", [("up_strand", list), ("down_strand", list)]
)

# datatype to store multiple domains' strand data in
# (this is a function that returns a DomainsContainer object whenever called)
DomainsContainer = lambda domain_count: tuple(
    StrandsContainer() for i in range(domain_count)
)
# the actual type (for type annotations)
DomainsContainerType: Tuple[StrandsContainerType, ...] = Tuple[StrandsContainerType]


class side_view:
    """
    Generate data needed for a side view graph of helicies.

    Attributes:
        interior_angles (List[float]): Angle between bases from a side view.
        base_height (float): Height between two bases (in Angstroms).
        interpoint_angle (int): The angle about the central axis going counter-clockwise from the line of tangency.
        strand_switch_distance (float): Strand strand_switch distance (in Angstroms).
        strand_switch_angle (float): The angle about the helix axis between two NEMids on different helices of a double helix.
        characteristic_angle (float, optional): Characteristic angle. Defaults to 360/21.
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
            interior_angle_multiples (list): Interbase angle interior, measured in multiples of characteristic angle.
            base_height (float): Height between two bases (in Angstroms).
            strand_switch_distance (float): Strand switch distance (in Angstroms).
            strand_switch_angle (float): Angle about the helix axis between two NEMids on different helices of a double helix.
            interpoint_angle_multiple (int, optional): Angle that one base makes about the helix axis, measured in multiples of characteristic angle.
            characteristic_angle (float, optional): Characteristic angle. Defaults to 360/21.

        Raises:
            ValueError: Length of interior_angles does not match that of strand_switch_angles.
        """
        self.domain_count = len(domains)

        self.characteristic_angle = characteristic_angle
        self.strand_switch_angle = strand_switch_angle
        self.interpoint_angle = interpoint_angle_multiple * self.characteristic_angle
        self.base_height = base_height
        self.strand_switch_distance = strand_switch_distance

        self.interior_angles = tuple(
            domain.interjunction_multiple * self.characteristic_angle
            for domain in domains
        )
        self.exterior_angles = tuple(360 - angle for angle in self.interior_angles)

    def point_angles(self, count: int, round_to=4, NEMid=False) -> DomainsContainerType:
        """
        Generate angles made about the central axis going counter-clockwise from the line of tangency for all points.
        Args:
            count (int): Number of interbase/NEMid (point) angles to generate.
            round_to (int): Decimal place to round output to.
            NEMid (bool, optional): Generate for NEMids instead of bases. Defaults to False (generate for bases).
        Returns:
            tuple: ([domain_0_up_strand], [domain_0_down_strand]), ([domain_1_up_strand], [domain_1_down_strand]), ...).
        """
        point_angles = DomainsContainer(self.domain_count)

        # set initial point angle values
        for domain_index in range(self.domain_count):
            point_angles[domain_index][0].append(0)
            point_angles[domain_index][1].append(0 - self.strand_switch_angle)

        # generate count# of point angles on a domain-by-domain basis
        # domain_index is the index of the current domain
        for domain_index in range(self.domain_count):
            for i in range(count):
                # only previous up strand point angle is needed to calculate the next point angle for up and down strands
                # [i] represents the previous one, since we are generating for the next one
                previous_up_strand_point_angle = point_angles[domain_index][0][i]

                # generate the next UP STRAND point angle
                # "point_angles[domain_index][0]" = point angles -> current domain -> list of point angles for up strand
                point_angles[domain_index][0].append(
                    previous_up_strand_point_angle + self.interpoint_angle
                )

                # generate the next DOWN STRAND point angle
                # "point_angles[domain_index][1]" = point angles -> current domain -> list of point angles for down strand
                point_angles[domain_index][1].append(
                    previous_up_strand_point_angle - self.strand_switch_angle
                )

        if NEMid:
            exec_on_innermost(
                point_angles, lambda point_angle: (point_angle - self.base_height / 2)
            )
        exec_on_innermost(
            point_angles, lambda point_angle: round(point_angle, round_to)
        )

        return point_angles

    @cache
    def x_coords(self, count: int, round_to=4, NEMid=False) -> DomainsContainerType:
        """
        Generate x cords.
        Args:
            count (int): Number of x cords to generate.
            round_to (int): Decimal place to round output to.
            NEMid (bool, optional): Generate for NEMids instead of bases. Defaults to False (generate for bases).
        Returns:
            tuple: ([domain_0_up_strand], [domain_0_down_strand]), ([domain_1_up_strand], [domain_1_down_strand]), ...).
        """
        x_coords: DomainsContainerType = DomainsContainer(
            self.domain_count
        )  # where to store the output/what to return
        point_angles: DomainsContainerType = self.point_angles(
            count
        )  # point angles are needed to convert to x coords

        # generate count# of x coords on a domain-by-domain basis
        # domain_index is the index of the current domain
        for domain_index in range(self.domain_count):
            for i in range(count):
                for strand_direction in range(
                    2
                ):  # repeat same steps for up and down strand
                    # find the current point_angle and modulo it by 360
                    # point angles are "the angle about the central axis going counter-clockwise from the line of tangency."
                    # they do not reset at 360, however, so we modulo the current point angle here
                    point_angle: float = (
                        point_angles[domain_index][strand_direction][i] % 360
                    )

                    # current exterior and interior angles ("tridomain" angles)
                    # note that "exterior_angle == 360 - interior_angle"
                    interior_angle: float = self.interior_angles[domain_index]
                    exterior_angle: float = self.exterior_angles[domain_index]

                    if point_angle < exterior_angle:
                        x_coord = point_angle / exterior_angle
                    else:
                        x_coord = (360 - point_angle) / interior_angle

                    # domain 0 lies between [0, 1] on the x axis
                    # domain 1 lies between [1, 2] on the x axis
                    # ext...
                    x_coord += domain_index

                    # store the new x_coord in the container object and continue
                    x_coords[domain_index][strand_direction].append(x_coord)

        exec_on_innermost(x_coords, lambda coord: round(coord, round_to))
        return x_coords

    @cache
    def z_coords(self, count: int, round_to=4, NEMid=False) -> DomainsContainerType:
        """
        Generate z cords.
        Args:
            count (int): Number of z cords to generate. Must be > 21 if generating for multiple domains.
            round_to (int): Decimal place to round output to.
            NEMid (bool, optional): Generate for NEMids instead of bases. Defaults to False (generate for bases).
        Returns:
            tuple: ([domain_0_up_strand], [domain_0_down_strand]), ([domain_1_up_strand], [domain_1_down_strand]), ...).
        Raises:
            Exception: Not enough domains. Count must be > 21 when multiple domains are passed.
        """
        # if there are multiple domains ensure "count" is over 21, because we would not be able to get a full
        # sample of the x coords for finding the best places to place NEMids/bases
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
        z_coords[0][0].append(0)
        z_coords[0][1].append(z_coords[0][0][0] - self.strand_switch_distance)

        # we cannot calcuate the z_coords for domains after the first one unless we find the z_coords for the first one first
        # the first domain has its initial z cords (up and down strands) set to (arbitrary) static values, whereas other domains do not
        # for all domains except domain#0 the initial z cord will rely on a specific z cord of the previous
        # and so, we calculate the z coords of domain#0...
        for i in range(count):
            # generate the next z_coord for the up strand...
            # append the previous z_coord + the base_height
            # "z_coords[0][0]" means "z_coords -> domain#0 -> up_strand -> (previous z_coord on the up strand of domain#0)"
            z_coords[0][0].append(z_coords[0][0][i] + self.base_height)

            # generate the next z_coord for the down strand...
            # append the previous z_coord's up strand value, minus the strand switch distance
            # "z_coords[0][0]" means "z_coords -> domain#0 -> down_strand -> (previous z_coord on the down strand of domain#0)"
            z_coords[0][1].append(z_coords[0][0][i] - self.strand_switch_distance)

        # now find and append the initial z_coord for each domain
        for domain_index in range(1, self.domain_count):
            previous_domain_index: int = domain_index - 1  # the previous domain's index

            # step 1: find the initial z cord for the current domain_index

            # lets find the maxmimum x cord for the previous domain
            # that will be the point where, when placed adjacently to the right in the proper place
            # there will be an overlap of NEMids/bases
            maximum_x_coord_index: DomainsContainerType = self.x_coords(
                21, NEMid=NEMid
            )  # 21 will get all the possible values of a given x cord
            # current structure is [[<up_strand>, <down_strand>], ...]
            # since we are aligning the new domain next to the previous, we index by <previous_domain_index>
            maximum_x_coord_index: List[float] = maximum_x_coord_index[
                previous_domain_index
            ][
                0
            ]  # we can sample the up strand

            # obtain the index of the maximum x coord
            maximum_x_coord_index: int = maximum_x_coord_index.index(
                max(maximum_x_coord_index)
            )

            # we are going to line up the next up strand so that its leftmost (first) point touches the previous domain's rightmost
            initial_z_coord: float = z_coords[previous_domain_index][0][
                maximum_x_coord_index
            ]

            # append this new initial z cord to the actual list of z_coords
            z_coords[domain_index][1].append(initial_z_coord)
            z_coords[domain_index][0].append(
                initial_z_coord + self.strand_switch_distance
            )

            # step 2: actually calculate the z coords of this new domain

            for i in range(count):  # (domain 0 is already calculated)
                # append the previous z_coord + the base_height
                # "z_coords[i][0][i]" == "z_coords -> domain#i -> up_strand -> (previous z_coord on up strand of domain#domain_index)"
                z_coords[domain_index][0].append(
                    z_coords[domain_index][0][i] + self.base_height
                )

                # append the previous z_coord's up strand value, minus the strand switch distance
                # "z_coords[i][0][i]" == "z_coords -> domain#i -> down_strand -> (previous z_coord on down strand of domain#domain_index)"
                z_coords[domain_index][1].append(
                    z_coords[domain_index][0][i] - self.strand_switch_distance
                )

        if NEMid:
            exec_on_innermost(z_coords, lambda cord: (cord - (self.base_height / 2)))
        exec_on_innermost(z_coords, lambda coord: round(coord, round_to))
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

        for domain_index in range(self.domain_count):
            if domain_index % 2:  # if the domain index is an even integer
                colors: tuple = ("r", "g")  # use red and green colors
            else:  # but if it is an odd integer
                colors: tuple = ("b", "y")  # use blue and yellow colors
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
                    self.x_coords(count)[domain_index][strand_direction],
                    self.z_coords(count)[domain_index][strand_direction],
                    title=title,  # name of what was just plotted
                    symbol=symbol,  # type of symbol (in this case up/down arrow)
                    symbolSize=6,  # size of arrows in px
                    pxMode=True,  # means that symbol size is in px
                    symbolPen=color,  # set color of pen to current color
                )

        main_plot.autoRange()  # reenable autorange so that it isn't zoomed out weirdly

        return plotted_window
