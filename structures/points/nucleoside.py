from dataclasses import dataclass
from types import NoneType
from typing import Union, Iterable

import pandas as pd

from constants import bases
from structures.points.point import Point


@dataclass
class Nucleoside(Point):
    """
    Nucleoside object.

    Attributes:
        base: The base of the nucleoside.
        complement: The complementary base of the nucleoside.
    """

    base: Union[bases.A, bases.T, bases.G, bases.C, bases.U, NoneType] = None

    def to_NEMid(self):
        """
        Convert the nucleoside to NEMid type.

        Loses all attributes that point to other Points.
        """
        from structures.points import NEMid

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
        """Return the complement of this base"""

        complements = {
            "A": "T",
            "T": "A",
            "C": "G",
            "G": "C",
            None: None,
        }
        return complements[self.base]

    def __repr__(self) -> str:
        return (
            f"nucleoside("
            f"pos={self.position() if self.position is not None else None}, "
            f"angle={round(self.angle, 3) if self.angle is not None else None}°, "
            f"base={str(self.base).replace('None', 'unset')}"
            f")"
        )


def export(
    nucleosides: Iterable[Nucleoside], filename: str | None
) -> None | pd.DataFrame:
    """
    Export many Nucleosides as either a pandas dataframe or a csv file.

    1) Points module's export() function is called to obtain a dataframe with
        all the Point data for all the NEMids passed.
    2) Extra columns for all Nucleoside specific data is added to the pandas dataframe.
    3) The Nucleosides passed are iterated through, and the data for each Nucleoside is
        added to the dataframe under the new column.
    """
    from structures.points.point import export as fetch_points_dataframe

    # Get the dataframe of all the Point data
    data = fetch_points_dataframe(nucleosides, filename=None)

    # Add the NEMid specific data to the dataframe
    data["nucleoside:base"] = [nucleoside.base for nucleoside in nucleosides]

    return data if filename is None else data.to_csv(filename, index=False)
