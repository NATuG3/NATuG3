from dataclasses import dataclass
from types import NoneType
from typing import Iterable, Union

import pandas as pd

from natug.constants import bases
from natug.constants.bases import COMPLEMENTS
from natug.structures.points.point import Point


@dataclass
class Nucleoside(Point):
    """
    Nucleoside object.

    Attributes:
        base: The base of the nucleoside.
        matching: The nucleoside on the other helix of the same double helix as this
            nucleoside that is at the same helical index as this nucleoside.
        complement: The complementary base of this nucleoside.
    """

    base: Union[bases.A, bases.T, bases.G, bases.C, bases.U, NoneType] = None

    @property
    def matching(self):
        try:
            other_helix = self.helix.other_helix()
            return other_helix.data.points[len(other_helix) - 1 - self.helical_index]
        except IndexError:
            return None

    @matching.setter
    def matching(self, value):
        other_helix = self.helix.other_helix()
        other_helix.data.points[len(other_helix) - 1 - self.helical_index] = value

    def __setattr__(self, key, value):
        """
        Restyle the nucleoside if a new base is set.
        """
        super().__setattr__(key, value)
        if key == "base" and self.styles is not None and self.strand is not None:
            self.styles.reset()

    def to_NEMid(self):
        """
        Convert the nucleoside to NEMid type.

        Loses all attributes that point to other Points.
        """
        from natug.structures.points import NEMid

        return NEMid(
            x_coord=self.x_coord,
            z_coord=self.z_coord,
            angle=self.angle,
            direction=self.direction,
            strand=self.strand,
            domain=self.domain,
        )

    @property
    def complement(self) -> str:
        """
        Return the complementary base of this Nucleoside's base.
        """
        return COMPLEMENTS[self.base]

    @complement.setter
    def complement(self, value):
        """Set the complement of this base"""
        self.base = COMPLEMENTS[value]

    def __repr__(self) -> str:
        return (
            f"Nucleoside("
            f"pos={self.position() if self.position is not None else None}, "
            f"angle={round(self.angle, 3) if self.angle is not None else None}°, "
            f"base={str(self.base).replace('None', 'unset')}"
            f")"
        )


def to_df(nucleosides: Iterable[Nucleoside]) -> None | pd.DataFrame:
    """
    Export the Nucleoside data to a pandas dataframe.

    1) Points module's export() function is called to obtain a dataframe with
        all the Point data for all the NEMids passed.
    2) Extra columns for all Nucleoside specific data is added to the pandas dataframe.
    3) The Nucleosides passed are iterated through, and the data for each Nucleoside is
        added to the dataframe under the new header.

    Args:
        nucleosides: The Nucleosides to export.

    Returns:
        None: If a filename is provided.
        pd.DataFrame: If a filename is not provided.
    """
    from natug.structures.points.point import to_df as fetch_points_dataframe

    # Get the dataframe of all the Point data
    data = fetch_points_dataframe(nucleosides)

    # Add the NEMid specific data to the dataframe
    data["nucleoside:base"] = [nucleoside.base for nucleoside in nucleosides]

    return data
