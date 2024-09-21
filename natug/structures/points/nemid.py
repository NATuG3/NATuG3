from dataclasses import dataclass
from typing import Iterable

import pandas as pd

from natug.structures.points.point import Point


@dataclass
class NEMid(Point):
    """
    NEMid object.

    Attributes:
        junctable: Whether this NEMid overlaps another NEMid and can thus can conjunct.
        juncmate: NEMid that can this NEMid can conjunct-with. NoneType if this no
            NEMid overlaps.
        junction: Whether this NEMid is a member of an active junction.
    """

    juncmate: None = None
    junctable: bool = False
    junction: bool = False

    def to_nucleoside(self):
        """
        Convert the nucleoside to NEMid type.

        Loses all attributes that point to other Points.
        """
        from natug.structures.points import Nucleoside

        return Nucleoside(
            x_coord=self.x_coord,
            z_coord=self.z_coord,
            angle=self.angle,
            direction=self.direction,
            strand=self.strand,
            domain=self.domain,
        )


def to_df(NEMids: Iterable[NEMid]) -> pd.DataFrame:
    """
    Export many NEMids as either a pandas dataframe or a csv file.

    1) Points module's export() function is called to obtain a dataframe with
        all the Point data for all the NEMids passed.
    2) Extra columns for all NEMid specific data is added to the pandas dataframe.
    3) The NEMids passed are iterated through, and the data for each NEMid is
        added to the dataframe under the new column.

    Args:
        NEMids: The NEMids to export.

    Returns:
        A pandas dataframe with all the NEMid data.
    """
    from natug.structures.points.point import to_df as fetch_points_dataframe

    # Get the dataframe of all the Point data
    data = fetch_points_dataframe(NEMids)

    # Add the NEMid specific data to the dataframe
    data["NEMid:junctable"] = [NEMid_.junctable for NEMid_ in NEMids]
    data["NEMid:junction"] = [NEMid_.junction for NEMid_ in NEMids]
    data["NEMid:juncmate"] = [
        (NEMid_.juncmate.uuid if NEMid_.juncmate is not None else None)
        for NEMid_ in NEMids
    ]

    return data
