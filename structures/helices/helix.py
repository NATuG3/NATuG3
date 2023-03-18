import itertools
from dataclasses import dataclass, field
from typing import Literal, Type, Iterable
from uuid import uuid4

import numpy as np
import pandas as pd

from constants.directions import UP, DOWN
from structures.points import NEMid, Nucleoside
from structures.profiles import NucleicAcidProfile
from structures.strands import Strand


@dataclass(slots=True)
class HelixData:
    """
    A container for the data of a helix.

    Attributes:
        helix: The helix that this data belongs to.
        x_coords: The x-coordinates of the points in the helix.
        z_coords: The z-coordinates of the points in the helix.
        angles: The angles of the points in the helix.
    """

    helix: Type["Helix"] | None = None

    x_coords: np.ndarray | None = None
    z_coords: np.ndarray | None = None
    angles: np.ndarray | None = None

    _data_arrays = ("x_coords", "z_coords", "angles")

    def size(self) -> int:
        """
        Get the size of the helix.

        Returns:
            The size of the helix.
        """
        assert len(self.x_coords) == len(self.z_coords) == len(self.angles)
        return len(self.x_coords)

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
        generation_count: The number of points to generate for the helix based off
            of its domain.
        double_helix: The double helix that this helix belongs to.
        domain: The domain that this helix lies within.
        data: The data of the helix. This is a HelixData object, and contains the
            x-coordinates, z-coordinates, and angles of the points in the helix.
        uuid: The unique identifier of the helix.
    """

    direction: Literal[UP, DOWN]
    double_helix: Type["DoubleHelix"] | None
    data: HelixData = field(default_factory=HelixData)
    uuid: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self):
        self.data.helix = self

    def __len__(self):
        """Return the number of points in the helix."""
        assert (
            len(self.data.x_coords) == len(self.data.z_coords) == len(self.data.angles)
        )
        return len(self.data.angles)

    @property
    def domain(self):
        """The domain that this helix lies within."""
        return self.double_helix.domain

    @property
    def generation_count(self):
        """The number of points to generate for the helix based off of its domain."""
        if self.double_helix.left_helix == self:
            return self.domain.left_helix_count
        elif self.double_helix.other_helix == self:
            return self.domain.other_helix_count
        else:
            raise ValueError(
                "Helix is not the zeroed OR other helix in its double helix."
            )

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
        for index, cls, angle, x_coord, z_coord in zip(
            itertools.count(),
            itertools.cycle(
                (NEMid, Nucleoside) if begin == NEMid else (Nucleoside, NEMid)
            ),
            self.data.angles,
            self.data.x_coords,
            self.data.z_coords,
        ):
            yield cls(  # type: ignore
                angle=angle,
                x_coord=round(x_coord, 5),
                z_coord=round(z_coord, 5),
                direction=self.direction,
                domain=domain,
                helix=self,
                helical_index=index,
            )

    def strand(
        self,
        nucleic_acid_profile: NucleicAcidProfile,
        begin: Literal[Nucleoside, NEMid] = Nucleoside,
        strand: Strand = None,
        **kwargs
    ) -> Strand:
        """
        Convert the strand builder to a Strand object.

        Args:
            nucleic_acid_profile: The nucleic acid profile to use for the strand.
            strand: The strand to fill with the data in the arrays. If None, a new
                strand is created and returned.
            begin: The type of the first item in the strand. Either Nucleoside or
                NEMid.
            **kwargs: Keyword arguments to pass to the Strand constructor.

        Returns:
            Strand: The strand with the data in the arrays. Either a new strand or
                the strand passed in.
        """
        strand = strand or Strand(
            nucleic_acid_profile=nucleic_acid_profile, helix=self, **kwargs
        )
        strand.extend(tuple(self.points(begin=begin)))
        return strand


def to_df(double_helices: Iterable[Helix]) -> pd.DataFrame:
    """
    Export many double helices to a pandas dataframe.

    Data for each double helix is stored in a row. The data for each double helix
    is stored in the following columns:
        "uuid": The UUID of the double helix.
        "data:domain": The UUID of the domain that the double helix lies within.
        "data:direction": The direction of the double helix. Either UP or DOWN.
        "data:generation_count": The number of points to generate for the double
            helix, in the form "bottom-body-top".
        "data:x_coords": The x-coordinates of the points in the double helix, separated
            by semicolons.
        "data:z_coords": The z-coordinates of the points in the double helix, separated
            by semicolons.
        "data:angles": The angles of the points in the double helix, separated by
            semicolons.

    Arguments:
        double_helices: All the double helices to be exported.

    Returns:
        A pandas dataframe containing data for many double helices.
    """
    count = len(double_helices)  # type: ignore
    data = {
        "uuid": np.empty(count, dtype=str),
        "data:domain": np.empty(count, dtype=str),
        "data:direction": np.empty(count, dtype=str),
        "data:generation_count": np.empty(count, dtype=str),
        "data:x_coords": np.empty(count, dtype=str),
        "data:z_coords": np.empty(count, dtype=str),
        "data:angles": np.empty(count, dtype=str),
    }
    for i, helix in enumerate(double_helices):
        data["uuid"][i] = helix.uuid
        data["data:domain"][i] = helix.domain.uuid
        data["data:direction"][i] = helix.direction
        data["data:generation_count"][i] = helix.generation_count.to_str()
        data["data:x_coords"][i] = np.array2string(helix.data.x_coords, separator=";")
        data["data:z_coords"][i] = np.array2string(helix.data.z_coords, separator=";")
        data["data:angles"][i] = np.array2string(helix.data.angles, separator=";")

    return pd.DataFrame(data)
