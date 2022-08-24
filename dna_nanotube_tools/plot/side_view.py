from typing import Iterable, List, Tuple
from dna_nanotube_tools.helpers import exec_on_innermost


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
        interior_angle_multiples: List[int],
        base_height: float,
        interpoint_angle: float,
        strand_switch_distance: float,
        strand_switch_angle: float,
        characteristic_angle=360 / 21,
    ) -> None:
        """
        Initilize side_view generation class.

        Args:
            interior_angle_multiples (list): Interbase angle interior, measured in multiples of characteristic angle.
            base_height (float): Height between two bases (in Angstroms).
            interpoint_angle (float): The angle that one base makes about the helix axis.
            strand_switch_distance (float): Strand switch distance (in Angstroms).
            strand_switch_angle (float): The angle about the helix axis between two NEMids on different helices of a double helix.
            characteristic_angle (float, optional): Characteristic angle. Defaults to 360/21.

        Raises:
            ValueError: Length of interior_angles does not match that of strand_switch_angles.
        """
        self.domain_count = len(interior_angle_multiples)

        self.characteristic_angle = characteristic_angle
        self.strand_switch_angle = strand_switch_angle
        self.interpoint_angle = interpoint_angle
        self.base_height = base_height
        self.strand_switch_distance = strand_switch_distance

        self.interior_angles = tuple(
            angle * self.characteristic_angle for angle in interior_angle_multiples
        )
        self.exterior_angles = tuple(360 - angle for angle in self.interior_angles)

        # container object to store data for up&down strand for all domains
        # this is a function so that it does not simply reference/modify self.container
        self.container = lambda: tuple([([], []) for i in range(self.domain_count)])

        # Note that "_cache" is appended to variables used by functions. Do not use these attributes directly; instead call related function.
        self.point_angle_cache = tuple(  # related function: point_angles()
            [tuple([[0], [0 - self.strand_switch_angle]])]
        )

    def point_angles(
        self, count: int, round_to=4, NEMid=False
    ) -> Tuple[Tuple[List[float], List[float]], ...]:
        """
        Generate angles made about the central axis going counter-clockwise from the line of tangency for all points.

        Args:
            count (int): Number of interbase/NEMid (point) angles to generate.
            round_to (int): Decimal place to round output to.
            NEMid (bool, optional): Generate for NEMids instead of bases. Defaults to False (generate for bases).

        Returns:
            tuple: ([domain_0_up_strand], [domain_0_down_strand]), ([domain_1_up_strand], [domain_1_down_strand]), ...).
        """
        point_angles = self.container()

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

    def x_coords(
        self, count: int, round_to=4, NEMid=False
    ) -> Tuple[Tuple[List[float], List[float]], ...]:
        """
        Generate x cords.

        Args:
            count (int): Number of x cords to generate.
            round_to (int): Decimal place to round output to.
            NEMid (bool, optional): Generate for NEMids instead of bases. Defaults to False (generate for bases).

        Returns:
            tuple: ([domain_0_up_strand], [domain_0_down_strand]), ([domain_1_up_strand], [domain_1_down_strand]), ...).
        """
        x_coords = self.container()  # where to store the output/what to return
        point_angles = self.point_angles(
            count
        )  # point angles are needed to convert to x coords

        # generate count# of x coords on a domain-by-domain basis
        # domain_index is the index of the current domain
        for domain_index in range(self.domain_count):
            for i in range(count):
                # find the current point_angle and modulo it by 360
                # point angles are "the angle about the central axis going counter-clockwise from the line of tangency."
                # they do not reset at 360, however, so we modulo the current point angle here
                point_angle = point_angles[domain_index][0][i] % 360

                # current exterior and interior angles ("tridomain" angles)
                # note that "exterior_angle == 360 - interior_angle"
                interior_angle = self.interior_angles[domain_index]
                exterior_angle = self.exterior_angles[domain_index]

                if point_angle < exterior_angle:
                    x_coord = point_angle / exterior_angle
                else:
                    x_coord = (360 - point_angle) / interior_angle

                # domain 0 lies between [0, 1] on the x axis
                # domain 1 lies between [1, 2] on the x axis
                # ext...
                x_coord += domain_index

                # store the new x_coord in the container object and continue
                x_coords[domain_index][0].append(x_coord)

            for coord in x_coords[domain_index][0]:
                x_coords[domain_index][1].append(coord) 

        exec_on_innermost(x_coords, lambda coord: round(coord, round_to))
        return x_coords

    def z_coords(
        self, count: int, round_to=4, NEMid=False
    ) -> Tuple[Tuple[List[float], List[float]], ...]:
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
        z_coords = self.container()

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
            previous_domain_index = domain_index - 1  # the previous domain's index

            # step 1: find the initial z cord for the current domain_index

            # lets find the maxmimum x cord for the previous domain
            # that will be the point where, when placed adjacently to the right in the proper place
            # there will be an overlap of NEMids/bases
            maximum_x_coord_index = self.x_coords(
                21, NEMid=NEMid
            )  # 21 will get all the possible values of a given x cord
            # current structure is [[<up_strand>, <down_strand>], ...]
            # since we are aligning the new domain next to the previous, we index by <previous_domain_index>
            maximum_x_coord_index = maximum_x_coord_index[previous_domain_index][
                0
            ]  # we can sample the up strand

            # obtain the index of the maximum x coord
            maximum_x_coord_index = maximum_x_coord_index.index(
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
