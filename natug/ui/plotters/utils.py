from functools import cache
from typing import Iterable, List, Tuple

import numpy as np
from PyQt6.QtGui import QFont, QPainterPath, QTransform


def dim_color(color: Iterable[int], factor: float):
    """
    Darken a color by a factor.

    Args:
        color (tuple): A tuple of 3-4 floats in the range 0-255.
        factor (float): A float in the range 0-1.
    """
    return [color * factor for color in list(color)]


def brighten_color(color: Iterable[int], factor: float):
    """
    Brighten a color by a factor.

    Args:
        color (tuple): A tuple of 3-4 floats in the range 0-255.
        factor (float): A float in the range 0-1.
    """
    return [color + (255 - color) * factor for color in list(color)]


@cache
def custom_symbol(
    symbol: str,
    font: QFont = QFont("Century"),
    flip=True,
    rotation: float = 0,
    scale: Tuple[float, float] | float = 1,
) -> QPainterPath:
    """
    Create custom symbol with font for pyqtgraph.

    Args:
        symbol: The symbol to create.
        font: The font to use.
        flip: Whether to flip the symbol.
        rotation: The rotation of the symbol.
        scale: The scale of the symbol.

    Returns:
        The symbol.

    Notes:
        This is a cached method, since symbols don't change.
        This method is from https://stackoverflow.com/a/70789822.
    """
    scale = (scale, scale) if isinstance(scale, float) else scale

    pg_symbol = QPainterPath()
    pg_symbol.addText(0, 0, font, symbol)
    br = pg_symbol.boundingRect()
    initial_scale = min(1.0 / br.width(), 1.0 / br.height())
    tr = QTransform()
    if flip:
        tr.scale(initial_scale, -initial_scale)
    else:
        tr.scale(initial_scale, initial_scale)

    # apply requested transformations
    tr.scale(scale, scale)
    tr.rotate(rotation)
    tr.translate(-br.x() - br.width() / 2.0, -br.y() - br.height() / 2.0)

    return tr.map(pg_symbol)


def chaikins_corner_cutting(
    coords: List[Tuple[float, float]] | np.ndarray, offset=0.25, refinements=5
):
    """
    Chaikin's corner cutting algorithm.

    This rounds all corners by "cutting" them <refinements> number of times.

    Args:
        coords: The coords to round the edges of.
        offset: The offset to use when rounding the edges.
        refinements: The number of times to perform the corner cutting algorithm.

    Returns:
        The rounded coords.

    Notes:
        Coords will be mutated
    """
    # https://stackoverflow.com/a/47255374
    coords = np.array(coords) if not isinstance(coords, np.ndarray) else coords

    for i in range(refinements):
        L = coords.repeat(2, axis=0)
        R = np.empty_like(L)
        R[0] = L[0]
        R[2::2] = L[1:-1:2]
        R[1:-1:2] = L[2::2]
        R[-1] = L[-1]
        coords = L * (1 - offset) + R * offset

    return coords
