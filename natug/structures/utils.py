from typing import List

import numpy as np

from natug.structures.points import NEMid, Nucleoside
from natug.structures.points.point import Point


def converge_point_data(
    angles, x_coords, z_coords, initial_type=NEMid, break_at: bool = None
) -> List[Point]:
    """
    Converge angles, x coords, and z coord arrays into a list of NEMids and
    nucleosides.

    Args:
        angles: The angles of the points.
        x_coords: The x coordinates of the points.
        z_coords: The z coordinates of the points.
        initial_type: The type of point to start with.
        break_at: The index to break at. If None, don't break.

    Returns:
        list: A list of alternating NEMids and Nucleosides set with the provided
            angles, x_coords, and z_coords.
    """
    # The output array.
    output = []

    # Generate the NEMid and Nucleoside objects.
    for counter, (angle, x_coord, z_coord) in enumerate(
        np.column_stack((angles, x_coords, z_coords)),
        start=(0 if initial_type == Nucleoside else 1),
    ):
        if counter == break_at:
            break
        if counter % 2:
            # If the counter is odd, we are generating a NEMid.
            item = NEMid(x_coord=x_coord, z_coord=z_coord, angle=angle)
        else:
            # If the counter is even, we are generating a Nucleoside.
            item = Nucleoside(x_coord=x_coord, z_coord=z_coord, angle=angle)
        output.append(item)

    return output
