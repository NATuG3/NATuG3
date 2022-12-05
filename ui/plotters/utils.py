from typing import Iterable


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
