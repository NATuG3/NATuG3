import itertools
import logging
from math import dist
from typing import List, Tuple

import settings
from constants.directions import *
from helpers import inverse
from structures.points import NEMid, Nucleoside
from structures.points.point import Point

logger = logging.getLogger(__name__)


class DomainStrandWorker:
    """
    Class for generating data needed for a side view graph of helices.
    This is used by the Domains structure to compute strands for its child workers.

    Attributes:
        domains: The domains to compute strands for.
        nucleic_acid_profile: The nucleic acid profile to use for computing strands.

    Methods:
        compute()
    """

    strand_directions = (UP, DOWN)
    cache_clearers = ("workers", "profiles")

    def __init__(self, domains: "Domains") -> None:
        """
        Initialize a side view generator object.

        Args:
            domains: The workers to compute sequencing for.
        """
        self.nucleic_acid_profile = domains.nucleic_acid_profile
        self.domains = domains

    def compute(
        self,
    ) -> List[Tuple[List[NEMid | Nucleoside], List[NEMid | Nucleoside]]]:
        """
        Compute all NEMid data.

        Returns:
            Strands object for all sequencing that the workers can create.
        """
        # the output container for all NEMids
        strands = [([], []) for _ in range(self.domains.count)]

        for index, domain in enumerate(self.domains.domains()):
            # how many NEMids to skip over for the up and down strand
            begin_at = [0, 0]

            for up_strand_z_coord in self._z_coords()[index][UP]:
                try:
                    # keep on moving the initial up-strand NEMid up until it begins above zero
                    if up_strand_z_coord < 0:
                        begin_at[UP] += 1
                    else:
                        # revert to the previous z coord
                        # (since the begin-at-up didn't tick)
                        up_strand_z_coord -= self.nucleic_acid_profile.Z_b
                        # then keep moving the initial down-strand NEMid up
                        # until it is within .094 nm of the up-strand's initial NEMid
                        # (determined above)
                        cycle = 0
                        for down_strand_z_coord in self._z_coords()[index][DOWN]:
                            cycle += 1
                            if (
                                abs(up_strand_z_coord - down_strand_z_coord)
                                > self.nucleic_acid_profile.Z_mate
                            ):
                                begin_at[DOWN] += 1
                                if cycle == 10000:
                                    logger.warning(
                                        "Cycle limit reached for lining up NEMids. "
                                        "This means a bad Z_mate was likely passed."
                                    )
                                    begin_at[DOWN] = 0
                                    raise StopIteration
                            else:
                                # break out of nested loop
                                raise StopIteration

                # allow breaking out of nested loop
                except StopIteration:
                    break

            # create this domain's data iterators
            angles = []
            x_coords = []
            z_coords = []

            # up-strand initial NEMid index; down-strand initial NEMid index
            for strand_direction, initial_index in enumerate(begin_at):
                # where to begin and end iterator (index)
                start = initial_index
                end = initial_index + domain.count

                # create iterators that begin and end at the correct indices
                angles.append(
                    tuple(
                        itertools.islice(
                            self._angles()[index][strand_direction], start, end
                        )
                    )
                )
                x_coords.append(
                    tuple(
                        itertools.islice(
                            self._x_coords()[index][strand_direction], start, end
                        )
                    )
                )
                z_coords.append(
                    tuple(
                        itertools.islice(
                            self._z_coords()[index][strand_direction], start, end
                        )
                    )
                )

            # create NEMid objects for final return DomainContainer
            for strand_direction in self.strand_directions:
                for angle, x_coord, z_coord in zip(
                    angles[strand_direction],
                    x_coords[strand_direction],
                    z_coords[strand_direction],
                ):
                    # combine all data into NEMid object
                    NEMid_ = NEMid(
                        x_coord=x_coord,
                        z_coord=z_coord,
                        angle=angle,
                        direction=strand_direction,
                        domain=domain,
                        strand=None,
                    )

                    # create a nucleoside object from the NEMid
                    nucleoside = NEMid_.to_nucleoside()

                    # rotate the nucloeside half a base rotation
                    nucleoside.angle += self.nucleic_acid_profile.theta_b / 2

                    # add half a base height to the nucleoside's z coord
                    nucleoside.z_coord += self.nucleic_acid_profile.Z_b / 2

                    # recompute the nucleoside's x coord
                    nucleoside.x_coord = Point.x_coord_from_angle(
                        nucleoside.angle, nucleoside.domain
                    )

                    # append the current NEMid and nucleoside to the to-be-outputted array
                    strands[index][strand_direction].append(NEMid_)
                    strands[index][strand_direction].append(nucleoside)

                if strand_direction == DOWN:
                    strands[index][strand_direction].reverse()

        # assign junctability and juncmates
        for index, domain in enumerate(self.domains.domains()):
            if index == self.domains.count - 1:
                next_strands = strands[0]
            else:
                next_strands = strands[index + 1]

            this_strands = strands[index]
            for strand1 in this_strands:
                for strand2 in next_strands:
                    # for the next up and down strand check every NEMid in our
                    # up and down strand to see if any NEMids are close to any
                    # of the next ones
                    for NEMid1 in strand1:
                        for NEMid2 in strand2:
                            junction = False
                            # if the two NEMids are very close consider it a junction
                            if (
                                dist(NEMid1.position(), NEMid2.position())
                                < settings.junction_threshold
                            ):
                                junction = True
                            # if the two NEMids are on opposite sides and have a very close
                            # vertical distance consider it a junction as well
                            else:
                                z_dist = abs(NEMid1.z_coord - NEMid2.z_coord)
                                x_dist = abs(NEMid1.x_coord - NEMid2.x_coord)
                                opposite_sides = (
                                    abs(x_dist - self.domains.count)
                                    < settings.junction_threshold
                                )
                                matching_heights = z_dist < settings.junction_threshold
                                if opposite_sides and matching_heights:
                                    junction = True

                            if junction:
                                NEMid1.juncmate = NEMid2
                                NEMid1.junctable = True
                                NEMid2.juncmate = NEMid1
                                NEMid2.junctable = True

        logger.debug("Created strands object from domains. Strands: %s", strands)

        return strands

    def _angles(self) -> List[Tuple[itertools.count, itertools.count]]:
        """
        Create generators that yield NEMid angles.

        Returns:
            A list of tuple(up-strand, down-strand) where up/down-strand are generators that yield floats.
        """
        angles = [[None, None] for _ in range(self.domains.count)]

        # generate count# of NEMid angles on a domain-by-domain basis
        # domain_index is the index of the current domain
        for index, domain in enumerate(self.domains.domains()):
            # look at left current domain helix joint
            zeroed_strand = domain.left_helix_joint

            # create infinite generators for the zeroed and non zeroed sequencing
            angles[index][zeroed_strand] = itertools.count(
                start=0.0,  # zeroed strand starts at 0
                step=self.nucleic_acid_profile.theta_b,  # and steps by self.theta_b
            )

            # calculate the start value of the inverse(zeroed_strand)
            if zeroed_strand == UP:
                start = 0.0 - self.nucleic_acid_profile.theta_s
            else:  # zeroed_strand == DOWN:
                start = 0.0 + self.nucleic_acid_profile.theta_s

            angles[index][inverse(zeroed_strand)] = itertools.count(
                start=start,  # non-zeroed strand starts at 0-self.theta_s
                step=self.nucleic_acid_profile.theta_b,  # and steps by self.theta_b
            )

        for index in range(self.domains.count):
            # tuplify the angles index
            angles[index] = tuple(angles[index])

        logger.debug("Created angles object from domains. Angles: %s", angles)

        return angles

    def _x_coords(self) -> List[Tuple[itertools.cycle, itertools.cycle]]:
        """
        Create a generator of X coords of NEMids for the side view plot.

        Returns:
            DomainsContainerType: A workers container with innermost entries of generators.
        """
        angles = self._angles()
        x_coords = [[[], []] for _ in range(self.domains.count)]

        # make a copy of the angles iterator for use in generating x coords
        for index, domain in enumerate(self.domains.domains()):
            # since every T NEMids the x coords repeat we only need to generate x coords for the first T NEMids
            for strand_direction in self.strand_directions:  # (UP, DOWN)
                for counter, angle in enumerate(angles[index][strand_direction]):
                    angle %= 360

                    x_coord = Point.x_coord_from_angle(angle, domain)

                    # store the new x_coord in the container object and continue
                    x_coords[index][strand_direction].append(x_coord)

                    # break once self.B x coords have been generated
                    if (
                        len(x_coords[index][strand_direction])
                        == self.nucleic_acid_profile.B
                    ):
                        break

                # there are self.B unique x coords
                # itertools.cycle infinitely loops through them
                x_coords[index][strand_direction] = itertools.cycle(
                    x_coords[index][strand_direction]
                )

            # tuplify the index
            x_coords[index] = tuple(x_coords[index])

        logger.debug("Created x_coords object from domains. X coords: %s", x_coords)

        return x_coords

    def _z_coords(self) -> List[Tuple[itertools.count, itertools.count]]:
        """
        Create a generator of Z coords of NEMids for the side view plot.

        Returns:
            DomainsContainerType: A workers container with innermost entries of generators.
        """
        x_coords = [list(domain) for domain in self._x_coords()]
        z_coords = [[None, None] for _ in range(self.domains.count)]

        # creating a sample of x coords
        for index, domain in enumerate(self.domains.domains()):
            for strand_direction in self.strand_directions:
                x_coords[index][strand_direction] = itertools.islice(
                    x_coords[index][strand_direction], 0, self.nucleic_acid_profile.B
                )
                x_coords[index][strand_direction] = tuple(
                    x_coords[index][strand_direction]
                )

        for index, domain in enumerate(self.domains.domains()):
            # look at the right joint of the previous domain
            # for calculating the initial z coord
            zeroed_strand = self.domains.domains()[index - 1].right_helix_joint

            # step 1: find the initial z cord for the current domain
            if index == 0:
                # this is the first domain
                # zero out the first domain's first NEMid
                initial_z_coord = 0
            else:
                # let's find and index of x coord where the (previous domain's x coord) == (this domain's index-1)
                # ...so if this is domain#2, let's find where domain#1 has an x coord of x=1 in its x coord list

                # generated the needed portion of the previous index's
                # z coords, of this domain's left helix joint (zeroed_strand)
                previous_z_coords = tuple(
                    itertools.islice(
                        z_coords[index - 1][zeroed_strand],
                        0,
                        self.nucleic_acid_profile.B,
                    )
                )

                # find the maximum x coord of the previous domain
                # (should be ~this domain's index - 1)
                initial_z_coord = max(x_coords[index - 1][zeroed_strand])

                # find the index of that x coord of the previous domain
                initial_z_coord = x_coords[index - 1][zeroed_strand].index(
                    initial_z_coord
                )

                # obtain the z coord of that index
                initial_z_coord = previous_z_coords[initial_z_coord]

            # move the initial Z coord down until it is as close to z=0 as possible
            # this way the graphs don't skew upwards weirdly
            offset_interval = (
                self.nucleic_acid_profile.Z_b * self.nucleic_acid_profile.B
            )
            while initial_z_coord > 0:
                initial_z_coord -= offset_interval
            initial_z_coord -= offset_interval

            # look at the left joint of the current domain
            # for calculating additional z coords
            zeroed_strand = domain.left_helix_joint

            # zeroed strand
            z_coords[index][zeroed_strand] = itertools.count(
                start=initial_z_coord, step=self.nucleic_acid_profile.Z_b
            )
            # begin at the initial z coord and step by self.Z_b

            # helix switch is the change in the z coord of a watson crick base pair
            # as we go from the left helix to the other helix (may not be left/right)
            helix_switch = self.nucleic_acid_profile.Z_s
            if zeroed_strand == UP:
                helix_switch *= -1
            # elif zeroed_strand == DOWN:
            #     helix_switch *= 1

            # non-zeroed strand
            z_coords[index][inverse(zeroed_strand)] = itertools.count(
                start=initial_z_coord + helix_switch, step=self.nucleic_acid_profile.Z_b
            )
            # begin at the (initial z coord - z switch) and step by self.Z_b

            # tuplify the index
            z_coords[index] = tuple(z_coords[index])

        logger.debug("Created z_coords object from domains. Z coords: %s", z_coords)

        return z_coords

    def __repr__(self) -> str:
        """
        Return a string representation of the side view worker.

        Includes:
            - the domains
            - the nucleic acid profile

        Returns:
            str: A string representation of the side view worker.
        """
        return f"SideViewWorker(domains={self.domains}, nucleic_acid_profile={self.nucleic_acid_profile})"

    def __len__(self):
        return self.domains.domains.count
