import itertools
from dataclasses import dataclass
from typing import Literal, Type

import numpy as np

from constants.directions import UP, DOWN
from structures.points import NEMid, Nucleoside
from structures.profiles import NucleicAcidProfile
from structures.strands import Strand


@dataclass(slots=True)
class HelixData:
    """
    A container for the data of a helix.

    Attributes:
        x_coords: The x-coordinates of the points in the helix.
        z_coords: The z-coordinates of the points in the helix.
        angles: The angles of the points in the helix.
    """

    x_coords: np.ndarray | None
    z_coords: np.ndarray | None
    angles: np.ndarray | None

    def __init__(self, size: int | None):
        """
        Initialize a container for the data of a helix.

        Args:
            size: The number of points in the helix.
        """
        if size is None:
            self.x_coords = None
            self.z_coords = None
            self.angles = None
        else:
            self.x_coords = np.zeros(size)
            self.z_coords = np.zeros(size)
            self.angles = np.zeros(size)

    def resize(self, size: int):
        """
        Resize the data arrays of the helix.

        Args:
            size: The new size of the helix.

        Notes:
            This method flushes the data of the helix. Use with caution.
        """
        self.x_coords = np.zeros(size)
        self.z_coords = np.zeros(size)
        self.angles = np.zeros(size)


@dataclass(slots=True)
class Helix:
    """
    A singular helix in a double helix.

    Attributes:
        direction: The direction of the helix. Either UP or DOWN.
        double_helix: The double helix that this helix belongs to.
        domain: The domain that this helix lies within.
        data: The data of the helix. This is a HelixData object, and contains the
            x-coordinates, z-coordinates, and angles of the points in the helix.
    """

    direction: Literal[UP, DOWN]
    double_helix: Type["DoubleHelix"] | None
    data: HelixData

    def __init__(
        self,
        direction: Literal[UP, DOWN],
        size: int | None,
        double_helix: Type["DoubleHelix"] | None = None,
    ):
        """
        Initialize a helix.

        Args:
            direction: The direction of the helix. Either UP or DOWN.
            size: The number of points in the helix. If None, the size can be set
                later with the resize method.
            double_helix: The double helix that this helix belongs to.
        """
        self.direction = direction
        self.double_helix = double_helix
        self.data = HelixData(size)

    @property
    def domain(self):
        """The domain that this helix lies within."""
        return self.double_helix.domain

    def point(self, type_: Literal[Type[Nucleoside], Type[NEMid]] = Nucleoside):
        """
        Obtain a specific point in the helix.

        Args:
            type_: The type of the point to return. Either Nucleoside or NEMid.
        """
        domain = self.double_helix.domain if self.double_helix else None
        return type_(
            angle=self.data.angles[0],  # type: ignore
            x_coord=self.data.x_coords[0],  # type: ignore
            z_coord=self.data.z_coords[0],  # type: ignore
            direction=self.direction,  # type: ignore
            domain=domain,  # type: ignore
        )

    def points(self, begin=Nucleoside):
        """
        Yield alternating NEMids and Nucleosides from the data in the arrays.

        Args:
            begin: The type of the first item yielded. Either Nucleoside or NEMid.

        Yields:
            Nucleoside or NEMid: The next item in the strand.
        """
        domain = self.double_helix.domain if self.double_helix else None
        for cls, angle, x_coord, z_coord in zip(
            itertools.cycle(
                (NEMid, Nucleoside) if begin == NEMid else (Nucleoside, NEMid)
            ),
            self.data.angles,
            self.data.x_coords,
            self.data.z_coords,
        ):
            yield cls(  # type: ignore
                angle=angle,
                x_coord=x_coord,
                z_coord=z_coord,
                direction=self.direction,
                domain=domain,
            )

    def strand(
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
        strand.extend(tuple(self.points()))
        return strand
