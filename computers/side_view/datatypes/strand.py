from functools import cached_property
from computers.datatypes import NEMid


class Strand:
    def __init__(self, strand: list):
        self._strand = tuple(strand)

    def from_coord(self, x_coord, z_coord) -> list[NEMid]:
        """Obtain a NEMid from a coord."""
        coord = (round(x_coord, 3), round(z_coord, 3))
        return self._by_coord.get(coord, None)

    @cached_property
    def _by_coord(self) -> dict[tuple[float, float], list[NEMid]]:
        _by_coord = dict()
        for NEMid_ in self._strand:
            coord = (round(NEMid_.x_coord, 3), round(NEMid_.z_coord, 3))
            if coord not in _by_coord:
                _by_coord[coord] = []
            _by_coord[coord].append(NEMid_)
        return _by_coord
