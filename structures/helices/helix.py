import itertools
from dataclasses import dataclass
from typing import Literal, Type

import numpy as np

from constants.directions import UP, DOWN
from structures.points import NEMid, Nucleoside
from structures.profiles import NucleicAcidProfile
from structures.strands import Strand


@dataclass(slots=True)
class Helix:
    """
    A singular helix in a double helix.

    The number of points allowed in the helix is fixed at init.

    Attributes:
        direction: The direction of the helix. Either UP or DOWN.
        x_coords: The x-coordinates of the points in the helix.
        z_coords: The z-coordinates of the points in the helix.
        angles: The angles of the points in the helix.
        size: The number of points in the helix. This is fixed at init.
    """

    def __init__(self, direction: Literal[UP, DOWN], size: int):
        """
        Initialize a helix.

        Args:
            direction: The direction of the helix. Either UP or DOWN.
            size: The number of points in the helix. This is fixed once set.
        """
        self.direction = direction
        self._size = size

        self.x_coords = np.zeros(self.size)
        self.z_coords = np.zeros(self.size)
        self.angles = np.zeros(self.size)

    @property
    def size(self):
        """The number of items in the given arrays of the helix."""
        return self._size

    def point(self, type_: Literal[Type[Nucleoside], Type[NEMid]] = Nucleoside):
        """
        Obtain a specific point in the helix.

        Args:
            type_: The type of the point to return. Either Nucleoside or NEMid.
        """
        return type_(
            angle=self.angles[0],  # type: ignore
            x_coord=self.x_coords[0],  # type: ignore
            z_coord=self.z_coords[0],  # type: ignore
            direction=self.direction,  # type: ignore
        )

    def points(self, begin=Nucleoside):
        """
        Yield alternating NEMids and Nucleosides from the data in the arrays.

        Args:
            begin: The type of the first item yielded. Either Nucleoside or NEMid.

        Yields:
            Nucleoside or NEMid: The next item in the strand.
        """
        for cls, angle, x_coord, z_coord in np.column_stack(
            itertools.cycle(
                (NEMid, Nucleoside) if begin == NEMid else (Nucleoside, NEMid)
            ),
            self.angles,
            self.x_coords,
            self.z_coords,
        ):
            yield cls(
                angle=angle,
                x_coord=x_coord,
                z_coord=z_coord,
                direction=self.direction,
            )

    def to_strand(
        self, nucleic_acid_profile: NucleicAcidProfile, strand: Strand = None
    ) -> Strand:
        """
        Convert the strand builder to a Strand object.

        Args:
            nucleic_acid_profile: The nucleic acid profile to use for the strand.
            strand: The strand to fill with the data in the arrays. If None, a new
                strand is created and returned.

        Returns:
            Strand: The strand with the data in the arrays. Either a new strand or
                the strand passed in.
        """
        strand = strand or Strand(nucleic_acid_profile=nucleic_acid_profile)
        strand.extend(self.points())
        return strand
