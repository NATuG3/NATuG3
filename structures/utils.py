from typing import List

import numpy as np

from structures.points import NEMid, Nucleoside
from structures.points.point import Point


def converge_point_data(angles, x_coords, z_coords, initial_type=Nucleoside) -> List[Point]:
    """
    Converge angles, x coords, and z coord arrays into a list of NEMids and
    nucleosides.

    Args:
        angles: The angles of the points.
        x_coords: The x coordinates of the points.
        z_coords: The z coordinates of the points.
        initial_type: The type of point to start with.

    Returns:
        list: A list of alternating NEMids and Nucleosides set with the provided
            angles, x_coords, and z_coords.
    """
    # The output array.
    output = []

    # Roughly equivalent to zipped = tuple(zip(angles, x_coords, z_coords)).
    zipped = np.column_stack((angles, x_coords, z_coords))

    if initial_type == Nucleoside:
        def counter_check(counter):
            return counter % 2 == 1
    else:
        def counter_check(counter):
            return counter % 2 == 0

    # Generate the NEMid and Nucleoside objects.
    for counter, (angle, x_coord, z_coord) in enumerate(zipped):
        if counter_check(counter):
            # If the counter is odd, we are generating a NEMid.
            item = NEMid(x_coord=x_coord, z_coord=z_coord, angle=angle)
            print(counter, NEMid)
        else:
            # If the counter is even, we are generating a Nucleoside.
            item = Nucleoside(x_coord=x_coord, z_coord=z_coord, angle=angle)
        output.append(item)

    return output
