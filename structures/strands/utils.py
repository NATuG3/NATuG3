from random import shuffle
from typing import Iterable


def rgb_to_hex(rgb):
    """Converts an (R, G, B) tuple to a hex string."""
    return f"#{int(rgb[0]):02x}{int(rgb[1]):02x}{int(rgb[2]):02x}"


def shuffled(iterable: Iterable) -> list:
    """Shuffle an iterable and return a copy."""
    output = list(iterable)
    shuffle(output)
    return output
