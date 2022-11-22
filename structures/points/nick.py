from typing import Tuple

from structures.points import NEMid


class Nick:
    """
    Nick object.

    Attributes:
        x_coord: X coord of the nick.
        z_coord: Z coord of the nick.
        prior: The object that this was before it became a nick.
    """

    def __init__(self, NEMid_: NEMid):
        self.x_coord, self.z_coord = NEMid_.x_coord, NEMid_.z_coord
        self.prior = NEMid_

    @classmethod
    def to_nick(cls, NEMid_):
        """Create a nick in the parent strand of NEMid_."""
        NEMid_.strand.NEMids[NEMid_.index] = cls(NEMid_)

    def position(self) -> Tuple[float, float]:
        """
        Obtain coords of the point as a tuple of form (x, z).
        """
        return self.x_coord, self.z_coord

    def __repr__(self) -> str:
        """Determine what to print when instance is printed directly."""
        return f"Nick@({self.position()})"
