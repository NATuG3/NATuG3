from typing import List, Tuple
from copy import deepcopy
import dna_nanotube_tools
import numpy as np


class side_view:
    """
    Generate data needed for a side view graph of helicies.

    Attributes:
        interior_angles (List[float]): Angle between bases from a side view.
        base_height (float): Height between two bases (in Angstroms).
        point_angle (int): The angle about the central axis going counter-clockwise from the line of tangency.
        strand_switch_distance (float): Strand strand_switch distance (in Angstroms).
        strand_switch_angle (float): The angle about the helix axis between two NEMids on different helices of a double helix.
        characteristic_angle (float, optional): Characteristic angle. Defaults to 360/21.
    """

    def __init__(
        self,
        interior_angle_multiples: List[int],
        base_height: float,
        point_angle: float,
        strand_switch_distance: float,
        strand_switch_angle: float,
        characteristic_angle=360 / 21,
    ) -> None:
        """
        Initilize side_view generation class.

        Args:
            interior_angle_multiples (list): Interbase angle interior, measured in multiples of characteristic angle.
            base_height (float): Height between two bases (in Angstroms).
            point_angle (float): The angle that one base makes about the helix axis.
            strand_switch_distance (float): Strand switch distance (in Angstroms).
            strand_switch_angle (float): The angle about the helix axis between two NEMids on different helices of a double helix.
            characteristic_angle (float, optional): Characteristic angle. Defaults to 360/21.

        Raises:
            ValueError: Length of interior_angles does not match that of strand_switch_angles.
        """
        self.domain_count = len(interior_angle_multiples)

        self.characteristic_angle = characteristic_angle
        self.strand_switch_angle = strand_switch_angle
        self.point_angle = point_angle
        self.base_height = base_height
        self.strand_switch_distance = strand_switch_distance

        self.interior_angles = tuple(
            angle * self.characteristic_angle for angle in interior_angle_multiples
        )
        self.exterior_angles = tuple(360 - angle for angle in self.interior_angles)

        # Note that "_cache" is appended to variables used by functions. Do not use these attributes directly; instead call related function.
        self.point_angle_cache = tuple(  # related function: point_angles()
            [tuple([[0], [0 - self.strand_switch_angle]])]
        )
        self.x_cache = tuple([tuple([[], []])])  # related function: x_coords()

    def point_angles(
        self, count: int, NEMid=False
    ) -> Tuple[Tuple[List[float], List[float]], ...]:
        """
        Generate angles between bases/NEMids ("points").

        Args:
            count (int): Number of interbase/NEMid (point) angles to generate.
            NEMid (bool, optional): Generate for NEMids instead of bases. Defaults to False (generate for bases).

        Returns:
            tuple: ([domain_0_up_strand], [domain_0_down_strand]), ([domain_1_up_strand], [domain_1_down_strand]), ...).
        """
        for i in range(count):
            for domain in self.point_angle_cache:
                # up strand
                domain[0].append(domain[0][i] + self.point_angle)
                # down strand
                domain[1].append(domain[0][i] - self.strand_switch_angle)

        if NEMid:
            return dna_nanotube_tools.helpers.exec_on_innermost(
                deepcopy(self.point_angle_cache),
                lambda cord: cord - (self.base_height / 2),
            )
        else:
            return self.point_angle_cache

    def x_coords(
        self, count: int, NEMid=False
    ) -> Tuple[Tuple[List[float], List[float]], ...]:
        """
        Generate x cords.

        Args:
            count (int): Number of x cords to generate.
            NEMid (bool, optional): Generate for NEMids instead of bases. Defaults to False (generate for bases).

        Returns:
            tuple: ([domain_0_up_strand], [domain_0_down_strand]), ([domain_1_up_strand], [domain_1_down_strand]), ...).
        """
        current = 0

        for i in range(count):
            for domain_index, domain in enumerate(self.x_cache):
                for strand_direction in range(
                    2
                ):  # [0, 1] 0 is up strand; 1 is down strand
                    if (  # if the next point angle is less than
                        self.point_angles(count + 1)[domain_index][strand_direction][
                            current
                        ]
                        % 360
                    ) < self.exterior_angles[domain_index]:
                        new_x = (
                            (
                                self.point_angles(count)[domain_index][
                                    strand_direction
                                ][current]
                            )
                            % 360
                        ) / self.exterior_angles[domain_index]
                    else:
                        new_x = (
                            (
                                360
                                - self.point_angles(count + 1)[domain_index][
                                    strand_direction
                                ][current]
                                % 360
                            )
                        ) / self.interior_angles[domain_index]

                    domain[strand_direction].append(new_x)
            current += 1

        return self.x_cache

    def z_coords(
        self, count: int, NEMid=False
    ) -> Tuple[Tuple[List[float], List[float]], ...]:
        """
        Generate z cords.

        Args:
            count (int): Number of z cords to generate. Must be > 21.
            NEMid (bool, optional): Generate for NEMids instead of bases. Defaults to False (generate for bases).

        Returns:
            tuple: ([domain_0_up_strand], [domain_0_down_strand]), ([domain_1_up_strand], [domain_1_down_strand]), ...).
        """
        # since all initial z_coord values are pre-set we reduce the count (which is used for itterating) by 1
        count -= 1 

        # create container all the z coords for each domain
        # each z cord is in the form [(<up_strand>, <down_strand>), ...]
        # tuple index is which domain it represents, and up_strand & down_strand are np.arrays of actual z coords
        z_coords = []

        # arbitrarily define the z_coord of the up strand of domain#0 to be 0
        z_coords.append([np.array(0.0), np.array(0.0 - self.strand_switch_distance)])

        # we cannot calcuate the z_coords for domains after the first one unless we find the z_coords for the first one first
        # the first domain has its initial z cords (up and down strands) set to (arbitrary) static values, whereas other domains do not
        # for all domains except domain#0 the initial z cord will rely on a specific z cord of the previous
        # and so, we calculate the z coords of domain#0...
        for i in range(count):
            # generate the next z_coord for the up strand...
            # append the previous z_coord + the base_height
            # "z_coords[0][0]" means "z_coords -> domain#0 -> up_strand -> (previous z_coord on the up strand of domain#0)"
            z_coords[0][0] = np.append(
                z_coords[0][0], z_coords[0][0] + self.base_height
            )

            # note:
            # weird quark with numpy is that when len(numpy_array) == 0 then numpy_array returns just the single value within it
            # and no numpy_array[-1] is needed 

            # generate the next z_coord for the down strand...
            # append the previous z_coord's up strand value, minus the strand switch distance
            # "z_coords[0][0]" means "z_coords -> domain#0 -> down_strand -> (previous z_coord on the down strand of domain#0)"
            z_coords[0][1] = np.append(
                z_coords[0][1], z_coords[0][1] - self.strand_switch_distance
            )

        # now find and append the initial z_coord for each domain
        for domain_index in range(self.domain_count - 1):
            # we already have the initial z_coord for domain 0
            # so, we do "range(self.domain_count - 1)" and "domain_index += 1"
            # because we are skipping domain 0 and its respective index (0)
            domain_index += 1

            # step 1: find the initial z cord for the current domain_index

            # lets find the maxmimum x cord for the previous domain
            # that will be the point where, when placed adjacently to the right in the proper place
            # there will be an overlap of NEMids/bases
            maximum_x_coord_index = self.x_coords(
                21
            )  # 21 will get all the possible values of a given x cord
            # current structure is [[<up_strand>, <down_strand>], ...]
            maximum_x_coord_index = maximum_x_coord_index[domain_index - 1][
                0
            ]  # we can sample the up strand of the current domain (domain_index)
            # WORK IN PROGRESS!!!! X CORDS WILL BE NUMPY ARRAYS EVENTUALLY, THEN THIS CAN BE UNCOMMENTED
                # # np.argmax finds the index(s) of the maximum element(s)
                # maximum_x_coord_index = np.argmax(maximum_x_coord_index)
            
            maximum_x_coord_index = maximum_x_coord_index.index(max(maximum_x_coord_index))

            # z_coords[domain_index-1] represents the previous domain's z_coords in the form [<up_strand>, <down_strand>]
            # we are going to line up the next up strand so that its leftmost (first) point touches that of the previous domain's
            initial_z_coord = z_coords[domain_index - 1][1][maximum_x_coord_index]

            # append this new initial z cord to the actual list of z_coords
            z_coords.append([np.array(initial_z_coord), np.array(initial_z_coord - self.strand_switch_distance)])
            # step 2: actually calculate the z coords of this new domain

            for i in range(count):
                # append the previous z_coord + the base_height
                # "z_coords[i][0][-1]" means "z_coords -> domain#i -> up_strand -> (previous z_coord on the up strand of domain#i)"
                z_coords[i][0] = np.append(
                    z_coords[i][0], z_coords[i][0][-1] + self.base_height
                )

                # append the previous z_coord's up strand value, minus the strand switch distance
                # "z_coords[i][0][-1]" means "z_coords -> domain#i -> down_strand -> (previous z_coord on the down strand of domain#i)"
                z_coords[i][1] = np.append(
                    z_coords[i][1], z_coords[i][1][-1] - self.strand_switch_distance
                )
        
        if NEMid:
            # z_coords for NEMids are the same but shifted down half a base height
            # (note that NEMids in reality are just the points in-between nemids)
            NEMid_modifier = (self.base_height / 2)
            for i in range(self.domain_count):
                z_coords[i][0] -= NEMid_modifier
                z_coords[i][1] -= NEMid_modifier

        return z_coords
