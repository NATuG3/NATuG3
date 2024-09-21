from dataclasses import dataclass, field
from typing import Iterable
from uuid import uuid1

import pandas as pd

from natug.structures.points.point import Point


@dataclass(slots=True)
class Nick:
    """
    A Nick object.

    All attributes of the original NEMid object are directly accessible through this
    object.

    Attributes:
        uuid: The unique identifier of the nick.
        original_item: The NEMid object that was transformed into a nick.
        previously_closed_strand: Whether the strand the nick used to belong to was
            closed.

    Methods:
        next_item: The next item along the helix that this nick is located in.
        previous_item: The previous item along the helix that this nick is located in.
    """

    original_item: Point
    previously_closed_strand: "Strand" = None

    uuid: str = field(default_factory=lambda: str(uuid1()))

    def next_item(self) -> "Point":
        return self.helix[self.helical_index + 1]

    def previous_item(self) -> "Point":
        return self.helix[self.helical_index - 1]

    def __getattr__(self, key: str) -> object:
        """
        When __getattribute__ fails, this method is called. This method searches for
        the attribute in the original NEMid object.
        """
        return getattr(self.original_item, key)

    def __repr__(self) -> str:
        """Determine what to print when instance is printed directly."""
        return f"Nick@{round(self.x_coord, 4), round(self.z_coord, 4)}"


def to_df(nicks: Iterable[Nick]) -> pd.DataFrame:
    """
    Export many Nicks as either a pandas dataframe or a csv file.

    Args:
        nicks: The Nicks to export.

    Returns:
        A pandas dataframe with all the Nick data.

    Notes:
        The original NEMid objects are referenced by uuid.
    """
    data = {
        "uuid": [nick.uuid for nick in nicks],
        "data:original_item": [nick.original_item.uuid for nick in nicks],
    }
    return pd.DataFrame(data)
