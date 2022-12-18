from typing import List

import numpy as np

from structures.points import NEMid, Nucleoside
from structures.points.point import Point


def converge_point_data(angles, x_coords, z_coords) -> List[Point]:
    """
    Converge angles, x coords, and z coord arrays into a list of NEMids and
    nucleosides.

    Returns:
        list: A list of alternating NEMids and Nucleosides set with the provided
            angles, x_coords, and z_coords.
    """
    # The output array.
    output = []

    # Roughly equivalent to zipped = tuple(zip(angles, x_coords, z_coords)).
    zipped = np.column_stack((angles, x_coords, z_coords))

    # Generate the NEMid and Nucleoside objects.
    for counter, (angle, x_coord, z_coord) in enumerate(zipped):
        if counter % 2:
            # If the counter is odd, we are generating a NEMid.
            item = NEMid(
                x_coord=x_coord, z_coord=z_coord, angle=angle
            )
        else:
            # If the counter is even, we are generating a Nucleoside.
            item = Nucleoside(
                x_coord=x_coord, z_coord=z_coord, angle=angle
            )
        output.append(item)

    return output
