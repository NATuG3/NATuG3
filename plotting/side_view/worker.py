from functools import lru_cache
from types import FunctionType
from typing import Deque, Tuple, Type
from collections import deque
from plotting.datatypes import NEMid


# container to store data for domains in
DomainsContainer: FunctionType = lambda domain_count: tuple(
    (deque(), deque()) for _ in range(domain_count)
)
# type annotation for the aforementioned container
DomainsContainerType: Type = Tuple[Tuple[Deque[float], Deque[float]], ...]


class Plot:
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
        Initialize side_view generation class.

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
                    # generate/retrieve cached
                    angle = self._NEMid_angles(count)[domain_index][strand_direction][i]
                    x_coord = self._x_coords(count)[domain_index][strand_direction][i]
                    z_coord = self._z_coords(count)[domain_index][strand_direction][i]

                    # combine all data into NEMid objects
                    _NEMid = NEMid(x_coord, z_coord, angle, None)
                    NEMids[domain_index][strand_direction].append(_NEMid)

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
            NEMid_angles[domain_index][0].append(0.0)
            NEMid_angles[domain_index][1].append(0.0 - self.theta_s)

            for i in range(count):

                # generate the next UP STRAND NEMid angle
                # "NEMid_angles[domain_index][0]" =
                # NEMid angles -> current domain -> list of NEMid angles for up strand -> previous one
                NEMid_angles[domain_index][0].append(
                    NEMid_angles[domain_index][0][i] + self.theta_b
                )

                # generate the next DOWN STRAND NEMid angle
                # "NEMid_angles[domain_index][0][i+1]" =
                # NEMid angles -> current domain -> list of NEMid angles for up strand -> one we just computed
                NEMid_angles[domain_index][1].append(
                    NEMid_angles[domain_index][0][i + 1] - self.theta_s
                )

        return NEMid_angles

    @lru_cache(maxsize=1)
    def _x_coords(self, count: int) -> DomainsContainerType:
        """Generate count# of x cords."""
        x_coords: DomainsContainerType = DomainsContainer(self.domain_count)
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

    def __repr__(self) -> str:
        output = "side_view("
        blacklist = "domains"
        for attr, value in vars(self).items():
            if attr not in blacklist:
                if isinstance(value, float):
                    value = round(value, 4)
                output += f"{attr}={value}, "
        output = output[:-2]
        output += ")"
        return output
