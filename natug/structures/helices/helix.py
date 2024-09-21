import itertools
import logging
from dataclasses import dataclass, field
from typing import Iterable, Literal, Type
from uuid import uuid1

import numpy as np
import pandas as pd

from natug.constants.directions import DOWN, UP
from natug.structures.domains.domain import GenerationCount
from natug.structures.points import NEMid, Nucleoside
from natug.structures.profiles import NucleicAcidProfile
from natug.structures.strands import Strand

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class HelixData:
    """
    A container for the data of a helix.

    Attributes:
        helix: The helix that this data belongs to.
        x_coords: The x-coordinates of the points in the helix.
        z_coords: The z-coordinates of the points in the helix.
        angles: The angles of the points in the helix.
        points: References to Point objects in the strand derived from this data.
        left_joint_points: The points that are on the left joint of the helix.
        right_joint_points: The points that are on the right joint of the helix.
    """

    helix: Type["Helix"] | None = None

    x_coords: np.ndarray | None = None
    z_coords: np.ndarray | None = None
    angles: np.ndarray | None = None
    points: np.ndarray | None = None
    left_joint_points: list = field(default_factory=list)
    right_joint_points: list = field(default_factory=list)

    _data_arrays = ("x_coords", "z_coords", "angles", "points")

    def __len__(self):
        return self.size()

    def size(self) -> int:
        """
        Get the size of the helix.

        Returns:
            The size of the helix.
        """
        return len(self.x_coords)

    def resize(self, size: int):
        """
        Resize the data arrays of the helix.

        Args:
            size: The new size of the helix.

        Notes:
            This method flushes the data of the helix. Use with caution.
        """
        logger.debug(f"Resizing helix data to %s points.", size)
        self.x_coords = np.zeros(size)
        self.z_coords = np.zeros(size)
        self.angles = np.zeros(size)
        self.points = np.zeros(size, dtype=object)


@dataclass(slots=True)
class Helix:
    """
    A singular helix in a double helix.

    Attributes:
        domain: The domain that the helix belongs to.
        counts: The generation count of the helix, which is stored in the parent domain.
        direction: The direction of the helix. Either UP or DOWN.
        double_helix: The parent DoubleHelix object.
        data: The data for the helix. This is a HelixData object that stores the
            actual positional and angle datapoints of all Points within the helix.
        uuid: The unique identifier of the helix.

    Methods:
        point: Generate a specific point object parented to this helix.
        points: Generate all the points along the helix.
        strand: Generate a strand full of points for this helix.
        other_helix: Obtain the other helix in the double helix.
    """

    direction: Literal[UP, DOWN]
    double_helix: Type["DoubleHelix"] | None
    data: HelixData = field(default_factory=HelixData)
    uuid: str = field(default_factory=lambda: str(uuid1()))

    def __post_init__(self):
        self.data.helix = self

    def __len__(self):
        """Return the number of points in the helix."""
        assert (
            len(self.data.x_coords) == len(self.data.z_coords) == len(self.data.angles)
        )
        return len(self.data.angles)

    def __getitem__(self, index: int) -> None:
        """Get a point at a given index along the helix."""
        return self.data.points[index]

    @property
    def domain(self):
        """The domain that this helix lies within."""
        return self.double_helix.domain

    @property
    def counts(self) -> GenerationCount:
        """
        The helix count for the given helix.

        This is a wrapper that returns either the domain's up_helix_count or
        down_helix_count.
        """
        if self.direction == UP:
            return self.domain.up_helix_count
        else:
            return self.domain.down_helix_count

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
        self.data.points = np.zeros(len(self.data.angles), dtype=object)
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
            point = cls(  # type: ignore
                angle=angle,
                x_coord=round(x_coord, 5),
                z_coord=round(z_coord, 5),
                direction=self.direction,
                domain=domain,
                helix=self,
                helical_index=index,
            )
            self.data.points[index] = point
            yield point

    def strand(
        self,
        nucleic_acid_profile: NucleicAcidProfile,
        begin: Literal[Nucleoside, NEMid] = Nucleoside,
        strand: Strand = None,
        **kwargs,
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

    def other_helix(self) -> "Helix":
        """
        Obtain the other helix in the double helix.

        Returns:
            Helix: The other helix in the double helix.
        """
        return self.double_helix[int(not bool(self.direction))]


def to_df(helices: Iterable[Helix]) -> pd.DataFrame:
    """
    Export many helices to a pandas dataframe.

    Data for each helix is stored in a row. The data for each helix
    is stored in the following columns:
        "uuid": The UUID of the helix.
        "data:domain": The UUID of the domain that the helix lies within.
        "data:direction": The direction of the helix. Either UP or DOWN.
        "data:generation_count": The number of points to generate for the double
            helix, in the form "bottom-body-top".
        "data:x_coords": The x-coordinates of the points in the helix, separated
            by semicolons.
        "data:z_coords": The z-coordinates of the points in the helix, separated
            by semicolons.
        "data:angles": The angles of the points in the helix, separated by
            semicolons.
        "data:points": The UUIDs of the points in the helix, separated by
            semicolons.

    Arguments:
        helices: All the double helices to be exported.

    Returns:
        A pandas dataframe containing data for many helices.
    """
    data = {
        "uuid": [],
        "data:double_helix": [],
        "data:direction": [],
        "data:x_coords": [],
        "data:z_coords": [],
        "data:angles": [],
        "data:points": [],
    }
    for helix in helices:
        data["uuid"].append(helix.uuid)
        data["data:double_helix"].append(helix.double_helix.uuid)
        data["data:direction"].append("UP" if helix.direction == UP else "DOWN")
        data["data:x_coords"].append(";".join(map(str, helix.data.x_coords)))
        data["data:z_coords"].append(";".join(map(str, helix.data.z_coords)))
        data["data:angles"].append(";".join(map(str, helix.data.angles)))
        data["data:points"].append(
            ";".join(map(lambda point: point.uuid, helix.data.points))
        )

    return pd.DataFrame(data)
