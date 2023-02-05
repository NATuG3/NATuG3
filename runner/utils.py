def rgb_to_hex(rgb):
    """
    Convert an rgb tuple to a hex code.

    Args:
        rgb: The rgb tuple to convert.

    Returns:
        str: The hex code.
    """
    # Make all the elements in the tuple integers
    return "#{:02x}{:02x}{:02x}".format(*[int(i) for i in rgb[:3]])


def hex_to_rgb(hex_code):
    """
    Convert a hex code to an rgb tuple.

    Args:
        hex_code: The hex code to convert.

    Returns:
        tuple: The rgb tuple.
    """
    return tuple(int(hex_code[i : i + 2], 16) for i in (1, 3, 5))
