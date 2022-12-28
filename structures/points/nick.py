from typing import Tuple

from structures.points import NEMid
from structures.points.point import Point


class Nick:
    """
    A Nick object.

    Contains the location of where the previous NEMid used to be before a nick was
    created, and the previous NEMid object (if the user wishes to undo the nick then
    the nick is converted back into a NEMid and is placed after the previous item).

    All attributes of the original NEMid object are directly accessible through this
    object.

    Attributes:
        previous_item: The NEMid object in the same strand as the original_NEMid.
        original_item: The NEMid object that was transformed into a nick.

    Methods:
        position: Obtain coords of the point as a tuple of form (x, z).
    """

    def __init__(self, original_item: Point):
        """
        Create a Nick object.

        Args:
            original_item: The Point object that is to be transformed into a nick.
                This object must be a child of a strand, so that the previous item can be
                found.
        """
        self.previous_item = original_item.strand[original_item.index - 1]
        self.original_item = original_item

    def __getattr__(self, key: str) -> object:
        """
        When __getattribute__ fails, this method is called. This method searches for
        the attribute in the original NEMid object.
        """
        return getattr(self.original_item, key)

    def __repr__(self) -> str:
        """Determine what to print when instance is printed directly."""
        return f"Nick@({round(self.x_coord, 4), round(self.z_coord, 4)})"
