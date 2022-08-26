from typing import Tuple, List

DomainsContainer = Tuple[Tuple[List[float], List[float]], ...]


class domain:
    """
    Domain storage object.

    Attributes:
        interjunction_multiple (int): The angle between two junctions on a double helix. Integer multiple of characteristic angle.
        switch_angle_multiple (int): Strand switch angle per domain transition. Integer multiple of strand switch angle.
        name (str): Name given to domain.
    """

    def __init__(self, interjunction_multiple: int, switch_angle_multiple: int) -> None:
        """
        Initilize domain storage class.

        Args:
            interjunction_multiple (int): The angle between two junctions on a double helix. Integer multiple of characteristic angle.
            switch_angle_multiple (int): Strand switch angle per domain transition. Integer multiple of strand switch angle.
        """
        self.name: str = ""
        self.interjunction_multiple: int = interjunction_multiple
        self.switch_angle_multiple: int = switch_angle_multiple
