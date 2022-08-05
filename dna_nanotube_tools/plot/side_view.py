from typing import List


class side_view:
    """
    Generate data needed for a side view graph of helicies.

    Attributes:
        interior_angles (List[float]): Angle between bases from a side view.
        base_height (float): Height between two bases (in Angstroms).
        base_angle (int): The angle that one base makes about the helix axis.
        strand_switch_distance (float): Strand strand_switch distance (in Angstroms).
        strand_switch_angle (float): The angle about the helix axis between two NEMids on different helices of a double helix.
        characteristic_angle (float, optional): Characteristic angle. Defaults to 360/21.
    """

    def __init__(
        self,
        interior_angle_multiples: List[int],
        base_height: float,
        base_angle: float,
        strand_switch_distance: float,
        strand_switch_angle: float,
        characteristic_angle=360 / 21,
    ) -> None:
        """
        Initilize side_view generation class.

        Args:
            interior_angle_multiples (list): Interbase angle interior, measured in multiples of characteristic angle.
            base_height (float): Height between two bases (in Angstroms).
            base_angle (int): The angle that one base makes about the helix axis.
            strand_switch_distance (float): Strand switch distance (in Angstroms).
            strand_switch_angle (float): The angle about the helix axis between two NEMids on different helices of a double helix.
            characteristic_angle (float, optional): Characteristic angle. Defaults to 360/21.

        Raises:
            ValueError: Length of interior_angles does not match that of strand_switch_angles.
        """
        self.characteristic_angle = characteristic_angle
        self.strand_switch_angle = strand_switch_angle
        self.base_angle = base_angle

        self.base_height = base_height
        self.strand_switch_distance = strand_switch_distance

        self.input_length = len(interior_angle_multiples)
        self.interior_angles = [
            angle * self.characteristic_angle for angle in interior_angle_multiples
        ]
        self.exterior_angles = [360 - angle for angle in self.interior_angles]

        # Note that "_cache" is appended to variables used by functions. Do not use these attributes directly; instead call related function.
        self.base_angle_cache = [  # related function: base_angles()
            [[0], [0 - self.strand_switch_angle]] * self.input_length
        ]
        self.x_cache = [[[], []] * self.input_length]  # related function: xs()
        self.z_cache = [
            [[0], [0 - self.strand_switch_distance]] * self.input_length
        ]  # related function: zs()

    def base_angles(self, count: int):
        """
        Generate angles between bases.

        Args:
            count (int): Number of interbase angles to generate.

        Returns:
            list: List of interbase angles in format [[[up strand], [down strand]], ...] for each domain.
        """
        current = 0
        while len(self.base_angle_cache[0][0]) < count:
            for domain in self.base_angle_cache:
                # up strand
                domain[0].append(domain[0][current] + self.base_angle)
                # down strand
                domain[1].append(domain[0][current + 1] - 2.3)
            current += 1
        return self.base_angle_cache

    def xs(self, count: int):
        """
        Generate x cords.

        Args:
            count (int): Number of x cords to generate.

        Returns:
            list: List of x cords in format [[[up strand], [down strand]], ...] for each domain.
        """
        current = 0
        while len(self.x_cache[0][0]) < count:
            for domain_index, domain in enumerate(self.x_cache):
                for strand_direction in range(2):
                    if (
                        self.base_angles(count + 1)[domain_index][strand_direction][
                            current
                        ]
                        < self.exterior_angles[domain_index]
                    ):
                        new_x = (
                            self.base_angles(count)[domain_index][strand_direction][
                                current
                            ]
                        ) / self.exterior_angles[domain_index]
                    else:
                        new_x = (
                            360
                            - self.base_angles(count + 1)[domain_index][
                                strand_direction
                            ][current]
                        ) / self.interior_angles[domain_index]
                    domain[strand_direction].append(new_x)
            current += 1
        return self.x_cache

    def zs(self, count: int):
        """
        Generate z cords.

        Args:
            count (int): Number of z cords to generate.

        Returns:
            list: List of z cords in format [[[up strand], [down strand]], ...] for each domain.
        """
        while len(self.z_cache[0][0]) < count:
            for domain in self.z_cache:
                # up strand
                domain[0].append(domain[0][-1] + self.base_height)
                # down strand
                domain[1].append(domain[0][-1] - self.strand_switch_distance)
        return self.z_cache
