from dataclasses import dataclass, field
from typing import Iterable
from uuid import uuid1

import pandas as pd

from structures.points.point import Point


@dataclass(slots=True)
class Nick:
    """
    A Nick object.

    Contains the location of where the previous NEMid used to be before a nick was
    created, and the previous NEMid object (if the user wishes to undo the nick then
    the nick is converted back into a NEMid and is placed after the previous item).

    All attributes of the original NEMid object are directly accessible through this
    object.

    Attributes:
        uuid: The unique identifier of the nick.
        previous_item: The NEMid object in the same strand as the original_NEMid.
        original_item: The NEMid object that was transformed into a nick.
    """

    original_item: Point
    previous_item: Point
    next_item: Point

    uuid: str = field(default_factory=lambda: str(uuid1()))

    def __getattr__(self, key: str) -> object:
        """
        When __getattribute__ fails, this method is called. This method searches for
        the attribute in the original NEMid object.
        """
        return getattr(self.original_item, key)

    def __repr__(self) -> str:
        """Determine what to print when instance is printed directly."""
        return f"Nick@{round(self.x_coord, 4), round(self.z_coord, 4)}"


def export(nicks: Iterable[Nick], filename: str | None) -> None | pd.DataFrame:
    """
    Export many Nicks as either a pandas dataframe or a csv file.

    Notes:
        The original NEMid objects are referenced by uuid.
    """
    data = {
        "uuid": [nick.uuid for nick in nicks],
        "original_item": [nick.original_item.uuid for nick in nicks],
        "previous_item": [nick.previous_item.uuid for nick in nicks],
        "next_item": [nick.next_item.uuid for nick in nicks],
    }
    df = pd.DataFrame(data)
    return df if filename is None else df.to_csv(filename, index=False)
