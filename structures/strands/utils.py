from random import shuffle
from typing import Iterable


def rgb_to_hex(rgb):
    """Converts an (R, G, B) tuple to a hex string."""
    return "#%02x%02x%02x" % rgb


def shuffled(iterable: Iterable) -> list:
    """Shuffle an iterable and return a copy."""
    output = list(iterable)
    shuffle(output)
    return output
