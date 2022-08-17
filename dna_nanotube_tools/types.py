from typing import Literal


class coords:
    """
    Stores cartesian coords.

    Attributes:
        xs (list): All x coords.
        ys (list): All y coords.
        pairs (function): Generator of all (x, y) pairs.
    """

    def __init__(self) -> None:
        self.xs = []
        self.ys = []
        self.pairs = lambda: zip(self.xs, self.ys)

    def add_coord(self, x: float, y: float) -> None:
        """
        Add coord set to object.

        Args:
            x (float): x cord to add
            y (float): y cord to add
        """
        self.xs.append(x)
        self.ys.append(y)

    def remove_coord(self, index: int) -> None:
        """
        Remove a coord given a specific index.

        Args:
            index (int): Index of coord to remove.
        """
        del self.xs[index]
        del self.ys[index]


class strand:
    def __init__(self, direction: Literal["up", "down"]) -> None:
        """
        Contains a single DNA strand.

        Args:
            direction (bool): True for up strand; False for down strand.
        """
        self.direction = direction
        if self.direction not in ("up", "down"):
            return TypeError("Invalid strand direction. Must be either up or down.")

        self.point_angles = []
        self.top_view_coords = coords()
        self.side_view_coords = coords()


class domain():
    """
    Domain storage object.
    """

    def __init__(self, interjunction_multiple: int, switch_angle_multiple: int) -> None:
        """
        Initilize domain storage class.

        Args:
            interjunction_multiple (int): The angle between two junctions on a double helix. Integer multiple of characteristic angle.
            switch_angle_multiple (int): Strand switch angle per domain transition. Integer multiple of strand switch angle.
        """
        self.interjunction_multiple = interjunction_multiple
        self.switch_angle_multiple = switch_angle_multiple

        self.up_strand = strand("up")
        self.down_strand = strand("down")
