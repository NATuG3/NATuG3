import itertools
from collections import deque
from contextlib import suppress
from functools import cached_property
from math import dist
from random import shuffle
from typing import Tuple, Type, Iterable, Deque

import settings
from structures.points import NEMid, Nucleoside
from structures.profiles import NucleicAcidProfile


def shuffled(iterable: Iterable) -> list:
    """Shuffle an iterable and return a copy."""
    output = list(iterable)
    shuffle(output)
    return output


class Strand:
    """
    A strand of items.

    Attributes:
        nucleic_acid_profile: The nucleic acid settings used.
        NEMids: All NEMids contained within the strand.
        nucleosides: All NEMids contained within the strand.
        color (tuple[int, int, int]): RGB color of strand.
        closed (bool): Whether the strand is closed. Must be manually set.
        empty (bool): Whether the strand is empty.
        up_strand (bool): Whether all NEMids in this strand are up-NEMids.
        down_strand (bool): Whether all NEMids in this strand are down-NEMids.
        interdomain (bool): Whether this strand spans multiple domains.
    """

    __cached = ("up_strand", "down_strand", "interdomain", "nucleosides")
    __supported_types = (NEMid, Nucleoside)

    def __init__(
        self,
        nucleic_acid_profile: NucleicAcidProfile,
        NEMids: Iterable[NEMid] | None = None,
        color: Tuple[int, int, int] = (0, 0, 0),
        closed: bool = False,
        parent: Type["Strands"] = None,
    ):
        """
        Initialize the strand object.

        Args:
            nucleic_acid_profile: The nucleic acid settings to use.
            NEMids: All NEMids to place inside the strand. Order sensitive.
            color: RGB color for the strand. Defaults to black.
            closed: Whether the strand is closed. Defaults to False.
            parent: The parent Strands object. Defaults to None.
        """
        self.color = color
        self.closed = closed
        self.parent = parent
        self.nucleic_acid_profile = nucleic_acid_profile

        if NEMids is None:
            self.NEMids = deque()
        else:
            self.NEMids = deque(NEMids)

        self.nucleosides = self.NEMids_to_nucleosides()

    def __len__(self) -> int:
        """Obtain number of items in strand."""
        return len(self.NEMids)

    def __contains__(self, item) -> bool:
        """Determine whether item is in strand."""
        return item in self.NEMids

    def NEMids_to_nucleosides(self) -> Deque[Nucleoside]:
        """
        Compute nucleosides from NEMids.

        Returns:
            A deque of nucleosides computed from the NEMids of the strand.
        """
        nucleosides: Deque[Nucleoside] = deque()
        previous_z_coord: float
        for NEMid_ in self.NEMids:
            previous_z_coord = NEMid_.z_coord
            z_has_changed = (
                abs(NEMid_.z_coord - previous_z_coord) < settings.junction_threshold
            )
            if not z_has_changed:
                nucleoside = Nucleoside(
                    x_coord=NEMid_.x_coord,
                    z_coord=NEMid_.z_coord + (self.nucleic_acid_profile.Z_b / 2),
                    angle=NEMid_.angle,
                    direction=NEMid_.direction,
                    base=None,
                    matching=NEMid_.matching,
                )
                nucleosides.append(nucleoside)
        return nucleosides

    def clear_pseudos(self) -> None:
        """Removes all pseudo items."""

        def pseudo_check(item):
            return not item.pseudo

        self.NEMids = deque(filter(pseudo_check, self.NEMids))
        self.nucleosides = deque(filter(pseudo_check, self.nucleosides))

    @property
    def index(self):
        """Obtain the index of this strand with respect to the parent strand. None if parent strand is None."""
        if self.parent is None:
            return None
        return self.parent.strands.index(self)

    def sliced(self, start: int, end: int) -> list:
        """Return self.NEMids as a list."""
        return list(itertools.islice(self.NEMids, start, end))

    def recompute(self) -> None:
        """Clear cached methods and reasign juncmates."""
        # clear all cache
        for cached in self.__cached:
            with suppress(KeyError):
                del self.__dict__[cached]

        # assign all our items to have us as their parent strand
        for index, NEMid_ in enumerate(self.NEMids):
            self.NEMids[index].strand = self

    def touching(self, other: Type["Strand"], touching_distance=0.2) -> bool:
        """
        Check whether this strand is touching a different strand.

        Args:
            other: The strand potentially touching this one.
            touching_distance: The distance to be considered touching.
        """
        for our_NEMid in shuffled(self.NEMids):
            for their_NEMid in shuffled(other.NEMids):
                if our_NEMid.juncmate is their_NEMid:
                    return True
        else:
            # we were not touching
            return False

    @property
    def empty(self) -> bool:
        """Whether this strand is empty."""
        return len(self.NEMids) == 0

    @cached_property
    def up_strand(self) -> bool:
        """Whether the strand is an up strand."""
        checks = [bool(NEMid_.direction) for NEMid_ in self.NEMids]
        return all(checks)

    @cached_property
    def down_strand(self) -> bool:
        """Whether the strand is a down strand."""
        checks = [(not bool(NEMid_.direction)) for NEMid_ in self.NEMids]
        return all(checks)

    @cached_property
    def interdomain(self) -> bool:
        """Whether all the NEMids in this strand belong to the same domain."""
        domains = [NEMid_.domain for NEMid_ in self.NEMids]

        if len(domains) == 0:
            return False
        checker = domains[0]
        for domain in domains:
            if domain != checker:
                return True
        return False

    @cached_property
    def size(self) -> Tuple[float, float]:
        """
        The overall size of the strand in nanometers.

        Returns:
            Tuple(width, height): The strand size.
        """
        width = max([item.x_coord for item in self.NEMids]) - min(
            [item.x_coord for item in self.NEMids]
        )
        height = max([item.z_coord for item in self.NEMids]) - min(
            [item.z_coord for item in self.NEMids]
        )
        return width, height
