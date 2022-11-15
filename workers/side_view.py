import itertools
import logging
from contextlib import suppress
from functools import cached_property, cache
from math import dist
from typing import List, Tuple

import settings
from constants.directions import *
from helpers import inverse
from structures.domains import Domains
from structures.misc import Profile
from structures.points import NEMid
from structures.strands.strand import Strand
from structures.strands.strands import Strands

logger = logging.getLogger(__name__)


class SideView:
    """
    Class for generating data needed for a side view graph of helices.
    """

    strand_directions = (UP, DOWN)
    cache_clearers = ("domains", "profiles")

    def __init__(self, domains: Domains, profile: Profile) -> None:
        """
        Initialize side_view generation class.
        """
        self.domains = domains
        assert isinstance(domains, Domains)
        self.profile = profile
        assert isinstance(profile, Profile)

    def __setattr__(self, key, value):
        if key in self.cache_clearers:
            self.clear_cache()
        super().__setattr__(key, value)

    def clear_cache(self):
        with suppress(KeyError):
            del self.__dict__["theta_exteriors"]
        with suppress(KeyError):
            del self.__dict__["theta_interiors"]
        self.compute.cache_clear()
        self.__repr__.cache_clear()

    @cached_property
    def theta_exteriors(self):
        theta_exteriors = []
        for theta_interior in self.theta_interiors:
            theta_exteriors.append(360 - theta_interior)
        return theta_exteriors

    @cached_property
    def theta_interiors(self):
        theta_interiors = []
        for domain in self.domains.domains:
            theta_interior = domain.theta_interior_multiple * self.profile.theta_c
            theta_interior -= domain.theta_switch_multiple * self.profile.theta_s
            theta_interiors.append(theta_interior)
        return theta_interiors

    @cache
    def compute(self) -> Strands:
        """
        Compute all NEMid data.

        Returns:
            List[Tuple[List[NEMid], List[NEMid]]]: List of tuple(up-strand, down-strand) for each domain.
        """
        # the output container for all NEMids
        NEMids = [([], []) for _ in range(self.domains.count)]

        for index, domain in enumerate(self.domains.domains):
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
                        up_strand_z_coord -= self.profile.Z_b
                        # then keep moving the initial down-strand NEMid up
                        # until it is within .094 nm of the up-strand's initial NEMid
                        # (determined above)
                        for down_strand_z_coord in self._z_coords()[index][DOWN]:
                            if abs(up_strand_z_coord - down_strand_z_coord) > 0.094:
                                begin_at[DOWN] += 1
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

                # append tuples of the properly spliced values
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
                    # if this NEMid is right on the domain line we can
                    # call it a "junctable" NEMid
                    if abs(x_coord - round(x_coord)) < settings.junction_threshold:
                        junctable = True
                    else:
                        junctable = False

                    # combine all data into NEMid object
                    NEMid_ = NEMid(
                        x_coord,
                        z_coord,
                        angle % 360,
                        strand_direction,
                        domain=domain,
                        junctable=junctable,
                    )

                    # append the current NEMid to the to-be-outputted array
                    NEMids[index][strand_direction].append(NEMid_)

                if strand_direction == DOWN:
                    NEMids[index][strand_direction].reverse()

        # assign matching NEMids to each other's matching slots
        for index, domain in enumerate(self.domains.domains):
            NEMid1: NEMid
            NEMid2: NEMid
            for NEMid1, NEMid2 in zip(*NEMids[index]):
                NEMid1.matching, NEMid2.matching = NEMid2, NEMid1

        strands = []
        for index, domain in enumerate(self.domains.domains):
            for strand_direction in self.strand_directions:
                strands.append(
                    Strand(
                        NEMids[index][strand_direction],
                        color=settings.colors["strands"]["greys"][strand_direction],
                    )
                )

        # set juncmates
        strands.sort(
            key=lambda strand: sum([item.x_coord for item in strand.items])
            / len(strand)
        )
        strands = Strands(strands)
        for index, strand in enumerate(strands.strands):
            if index < len(strands) - 1:
                for this_strand_item in strand.items:
                    for next_strand_item in strands.strands[index + 1].items:
                        if (
                            dist(
                                this_strand_item.position(), next_strand_item.position()
                            )
                            < settings.junction_threshold
                        ):
                            this_strand_item.juncmate = next_strand_item
                            next_strand_item.juncmate = this_strand_item

        # assign strands to NEMids
        for strand in strands.strands:
            strand.recompute()

        return strands

    def _angles(self) -> List[Tuple[itertools.count, itertools.count]]:
        """
        Create a generator of angles for NEMids in the side view plot.

        Returns:
            DomainsContainerType: A domains container with innermost entries of generators.
        """
        angles = [[None, None] for _ in range(self.domains.count)]

        # generate count# of NEMid angles on a domain-by-domain basis
        # domain_index is the index of the current domain
        for index, domain in enumerate(self.domains.domains):
            # look at left current domain helix joint
            zeroed_strand = domain.helix_joints[LEFT]

            # create infinite generators for the zeroed and non zeroed strands
            angles[index][zeroed_strand] = itertools.count(
                start=0.0,  # zeroed strand starts at 0
                step=self.profile.theta_b,  # and steps by self.theta_b
            )

            # calculate the start value of the inverse(zeroed_strand)
            if zeroed_strand == UP:
                start = 0.0 - self.profile.theta_s
            else:  # zeroed_strand == DOWN:
                start = 0.0 + self.profile.theta_s

            angles[index][inverse(zeroed_strand)] = itertools.count(
                start=start,  # non-zeroed strand starts at 0-self.theta_s
                step=self.profile.theta_b,  # and steps by self.theta_b
            )

        for index in range(self.domains.count):
            # tuplify the angles index
            angles[index] = tuple(angles[index])

        return angles

    def _x_coords(self) -> List[Tuple[itertools.cycle, itertools.cycle]]:
        """
        Create a generator of X coords of NEMids for the side view plot.

        Returns:
            DomainsContainerType: A domains container with innermost entries of generators.
        """
        angles = self._angles()
        x_coords = [[[], []] for _ in range(self.domains.count)]

        # make a copy of the angles iterator for use in generating x coords
        for index, domain in enumerate(self.domains.domains):
            # since every T NEMids the x coords repeat we only need to generate x coords for the first T NEMids
            for strand_direction in self.strand_directions:  # (UP, DOWN)
                for counter, angle in enumerate(angles[index][strand_direction]):
                    angle %= 360

                    theta_interior = self.theta_interiors[index]
                    theta_exterior = self.theta_exteriors[index]

                    if angle < self.theta_exteriors[index]:
                        x_coord = angle / theta_exterior
                    else:
                        x_coord = (360 - angle) / theta_interior

                    # domain 0 lies between [0, 1] on the x axis
                    # domain 1 lies between [1, 2] on the x axis
                    # ext...
                    x_coord += index

                    # store the new x_coord in the container object and continue
                    x_coords[index][strand_direction].append(x_coord)

                    # break once self.B x coords have been generated
                    if len(x_coords[index][strand_direction]) == self.profile.B:
                        break

                # there are self.B unique x coords
                # itertools.cycle infinitely loops through them
                x_coords[index][strand_direction] = itertools.cycle(
                    x_coords[index][strand_direction]
                )

            # tuplify the index
            x_coords[index] = tuple(x_coords[index])

        return x_coords

    def _z_coords(self) -> List[Tuple[itertools.count, itertools.count]]:
        """
        Create a generator of Z coords of NEMids for the side view plot.

        Returns:
            DomainsContainerType: A domains container with innermost entries of generators.
        """
        x_coords = [list(domain) for domain in self._x_coords()]
        z_coords = [[None, None] for _ in range(self.domains.count)]

        # creating a sample of x coords
        for index, domain in enumerate(self.domains.domains):
            for strand_direction in self.strand_directions:
                x_coords[index][strand_direction] = itertools.islice(
                    x_coords[index][strand_direction], 0, self.profile.B
                )
                x_coords[index][strand_direction] = tuple(
                    x_coords[index][strand_direction]
                )

        for index, domain in enumerate(self.domains.domains):
            # look at the right joint of the previous domain
            # for calculating the initial z coord
            zeroed_strand = self.domains.domains[index - 1].helix_joints[RIGHT]

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
                        z_coords[index - 1][zeroed_strand], 0, self.profile.B
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
            offset_interval = self.profile.Z_b * self.profile.B
            while initial_z_coord > 0:
                initial_z_coord -= offset_interval
            initial_z_coord -= offset_interval

            # look at the left joint of the current domain
            # for calculating additional z coords
            zeroed_strand = domain.helix_joints[LEFT]

            # zeroed strand
            z_coords[index][zeroed_strand] = itertools.count(
                start=initial_z_coord, step=self.profile.Z_b
            )
            # begin at the initial z coord and step by self.Z_b

            # helix switch is the change in the z coord of a watson crick base pair
            # as we go from the left helix to the other helix (may not be left/right)
            helix_switch = self.profile.Z_s
            if zeroed_strand == UP:
                helix_switch *= -1
            # elif zeroed_strand == DOWN:
            #     helix_switch *= 1

            # non-zeroed strand
            z_coords[index][inverse(zeroed_strand)] = itertools.count(
                start=initial_z_coord + helix_switch, step=self.profile.Z_b
            )
            # begin at the (initial z coord - z switch) and step by self.Z_b

            # tuplify the index
            z_coords[index] = tuple(z_coords[index])

        return z_coords

    @cache
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

    def __len__(self):
        return self.domains.domains.count
