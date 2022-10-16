import itertools
from typing import Generator, List
from copy import copy
from functools import cached_property
from types import FunctionType
from typing import Tuple, Type

from computers.datatypes import NEMid
from computers.side_view.interface import Plotter
from constants.directions import *
from helpers import inverse

# container to store data for domains in
DomainsContainer: FunctionType = lambda count: [[[], []] for _ in range(count)]

# type annotation for the aforementioned container
DomainsContainerType: Type = Tuple[Tuple[Generator, Generator], ...]


class SideView:
    """
    Generate data needed for a side view graph of helices.

    NEMid_angles (DomainsContainerType): All NEMid angles.
    x_coords (DomainsContainerType): All x coords.
    z_coords (DomainsContainerType) All z coords.
    """

    def __init__(
            self,
            domains: list,
            T: float,
            B: int,
            H: float,
            Z_s: float,
            theta_s: float,
            theta_b: float,
            theta_c: float,
    ) -> None:
        """
        Initialize side_view generation class.

        Args:
            domains (list): List of domains.
            T (int): There are T turns per B bases.
            B (int): There are B bases per T turns.
            H (float): Height of one helical twist.
            Z_s (float): Strand switch distance (in nm).
            theta_s (float): Switch angle (in degrees).
            theta_b (float): Base angle (in degrees).
            theta_c (float): Characteristic angle (in degrees).
        """
        self.domains = domains

        self.T = T
        self.B = B
        self.H = H

        self.Z_b = (T * H) / B
        self.Z_s = Z_s

        self.theta_s = theta_s
        self.theta_b = theta_b
        self.theta_c = theta_c

        self.strand_directions = (UP, DOWN)

        # containers for class property workers to generate into
        self._angles: DomainsContainerType = DomainsContainer(len(self.domains))
        self._x_coords: DomainsContainerType = DomainsContainer(len(self.domains))
        self._z_coords: DomainsContainerType = DomainsContainer(len(self.domains))

        # the extra bases to trim (as a byproduct of z_coord generation)
        self._extraneous_bases: Tuple[List[int, int], ...] = tuple([[0, 0] for domain in self.domains])

    def compute(self) -> DomainsContainerType:
        """
        Compute NEMid data.

        Returns:
            DomainsContainerType: A domains container of all NEMids.
        """

        NEMids = DomainsContainer(len(self.domains))

        for index, domain in enumerate(self.domains):
            for strand_direction in self.strand_directions:
                angles = itertools.islice(self.angles[index][strand_direction], 0, domain.count)
                x_coords = itertools.islice(self.x_coords[index][strand_direction], 0, domain.count)
                z_coords = itertools.islice(self.z_coords[index][strand_direction], 0, domain.count)

                for angle, x_coord, z_coord in zip(angles, x_coords, z_coords):
                    # combine all data into NEMid object
                    _NEMid = NEMid(x_coord, z_coord, angle, None)

                    # append the current NEMid to the to-be-outputted array
                    NEMids[index][strand_direction].append(_NEMid)

        return NEMids

    @cached_property
    def angles(self) -> DomainsContainerType:
        # generate count# of NEMid angles on a domain-by-domain basis
        # domain_index is the index of the current domain
        for index, domain in enumerate(self.domains):
            # which strand will begin at x=0 (+domain_index)
            zeroed_strand = domain.helix_joints[LEFT]

            # create infinite generators for the zeroed and non zeroed strands
            self._angles[index][zeroed_strand] = itertools.count(
                start=0.0,  # zeroed strand starts at 0
                step=self.theta_b,  # and steps by self.theta_b
            )
            self._angles[index][inverse(zeroed_strand)] = itertools.count(
                start=0.0 - self.theta_s,  # non-zeroed strand starts at 0-self.theta_s
                step=self.theta_b,  # and steps by self.theta_b
            )

        output = copy(self._angles)
        for index, domain in enumerate(self.domains):
            for strand_direction in self.strand_directions:
                output[index][strand_direction] = tuple(
                    itertools.islice(output[index][strand_direction], 0, domain.count)
                )

        return self._angles

    @cached_property
    def x_coords(self) -> DomainsContainerType:
        # make container for output
        output = copy(self._x_coords)

        # make a copy of the angles iterator for use in generating x coords
        for index, domain in enumerate(self.domains):
            # current exterior and interior angles
            theta_interior: float = domain.theta_interior_multiple * self.theta_c
            theta_exterior: float = 360 - theta_interior

            # since every T NEMids the x coords repeat we only need to generate x coords for the first T NEMids
            for strand_direction in self.strand_directions:
                for i in range(domain.count):
                    # find the current NEMid_angle and modulo it by 360 NEMid angles are "the angle about the central
                    # axis going counter-clockwise from the line of tangency." they reset at 360, so we modulo the
                    # current NEMid angle here
                    NEMid_angle: float = self.angles[index][strand_direction][i] % 360

                    if NEMid_angle < theta_exterior:
                        x_coord = NEMid_angle / theta_exterior
                    else:
                        x_coord = (360 - NEMid_angle) / theta_interior

                    # domain 0 lies between [0, 1] on the x axis
                    # domain 1 lies between [1, 2] on the x axis
                    # ext...
                    x_coord += index

                    # store the new x_coord in the container object and continue
                    self._x_coords[index][strand_direction].append(x_coord)

            self._x_coords[index][strand_direction] = itertools.cycle(self._x_coords[index][strand_direction])

        return self._x_coords

    @cached_property
    def z_coords(self) -> DomainsContainerType:
        for index, domain in enumerate(self.domains):
            # look at the right joint of the previous domain
            # for calculating the initial z coord
            zeroed_strand = self.domains[index - 1].helix_joints[RIGHT]

            # step 1: find the initial z cord for the current domain
            if index == 0:
                # this is the first domain
                # zero out the first domain's first NEMid
                initial_z_coord = 0

                # extra bases for first domain is zero
                extra_bases = 0
            else:
                # let's find and index of x coord where the (previous domain's x coord) == (this domain's index-1)
                # ...so if this is domain#2, let's find where domain#1 has an x coord of x=1 in its x coord list

                x_coords = tuple(itertools.islice(self.x_coords[index - 1][zeroed_strand], 0, self.B))

                # find the maximum x coord of the previous domain
                # (should be ~this domain's index - 1)
                initial_z_coord = max(x_coords)

                # find the index of that x coord of the previous domain
                initial_z_coord = x_coords.index(
                    initial_z_coord
                )

                # obtain the z coord of that index
                initial_z_coord = self._z_coords[index - 1][zeroed_strand][
                    initial_z_coord
                ]

                # move the initial Z coord down until it is as close to z=0 as possible
                # this way the graphs don't skew upwards weirdly
                # offset_amount = self.B * self.Z_b
                # while initial_z_coord > 0:
                #     initial_z_coord -= offset_amount

            # look at the left joint of the current domain
            # for calculating additional z coords
            zeroed_strand = domain.helix_joints[LEFT]

            # zeroed strand
            self._z_coords[index][zeroed_strand] = itertools.count(
                start=initial_z_coord,
                step=self.Z_b
            )
            self._z_coords[index][zeroed_strand] = tuple(
                itertools.islice(self._z_coords[index][zeroed_strand], 0, domain.count)
            )

            # non-zeroed strad
            self._z_coords[index][inverse(zeroed_strand)] = itertools.count(
                start=initial_z_coord - self.Z_s,
                step=self.Z_b
            )
            self._z_coords[index][inverse(zeroed_strand)] = tuple(
                itertools.islice(self._z_coords[index][inverse(zeroed_strand)], 0, domain.count)
            )

        return self._z_coords

    @cached_property
    def extraneous_bases(self):
        for index, domain in enumerate(self.domains):
            for strand_direction in self.strand_directions:
                while (
                        self.z_coords[index][strand_direction][0] + (self.extraneous_bases[index] * self.Z_b)
                ) < 0:
                    self.extraneous_bases[index][strand_direction] += 1
        return self._extraneous_bases

    def ui(self):
        return Plotter(self)

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

    def __eq__(self, other) -> bool:
        if not isinstance(other, type(self)):
            return False

        if len(self.domains) != len(other.domains):
            return False

        for our_domain, their_domain in zip(self.domains):
            if our_domain != their_domain:
                return False

        return True
