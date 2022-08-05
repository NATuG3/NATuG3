from typing import List


class side_view:
    """
    Generate (x, z) cords for side view of helices generation.
    """

    def __init__(
        self,
        interior_angles: List[int],
        switch_angles: List[int],
        z_distance: float,
        switch_distance: float,
        switch_theta: float,
        base_angle: int,
        theta_c=360 / 21,
        theta_s=0,
    ) -> None:
        """
        Initilize side_view generation class.

        Args:
            interior_angles (list): Theta interior, measured in multiples of characteristic angle.
            switch_angles (list): List of multiples of switch angle.
            z_distance (float): distance between bases (in Angstroms).
            switch_distance (float): Strand switch distance (in Angstroms).
            switch_theta (float): Strand switch angle (theta) (in degrees).
            base_angle (int): Angle between bases, measured in multiples of characteristic angle.
            theta_c (float, optional): Characteristic angle. Defaults to 360/21.
            theta_s (float, optional): Switch angle. Defaults to 0.
        Raises:
            ValueError: Length of interior_angles does not match that of switch_angles.
        """
        if len(interior_angles) != len(switch_angles):
            raise ValueError("len(interior_angles) != len(switch_angles)")

        self.theta_c = theta_c
        self.theta_s = theta_s
        self.z_distance = z_distance
        self.switch_distance = switch_distance
        self.switch_theta = switch_theta
        self.base_angle = base_angle * theta_c

        self.input_length = len(interior_angles)

        self.interior_angles = [angle*self.theta_c for angle in interior_angles]
        self.exterior_angles = [360 - angle for angle in self.interior_angles]
        self.switch_angles = switch_angles

        self.theta_list = [[[0], [0 - self.switch_theta]] * self.input_length]
        self.x_list = [[[], []] * self.input_length]
        self.z_list = [[[0], [0 - self.switch_distance]] * self.input_length]

    def thetas(self, count: int):
        """
        Generate thetas.

        Args:
            count (int): Number of thetas to generate.

        Returns:
            list: List of thetas in format [[[up strand], [down strand]], ...] for each domain.
        """
        current = 0
        while len(self.theta_list[0][0]) < count:
            for domain_index, domain in enumerate(self.theta_list):
                # up strand
                domain[0].append(
                    domain[0][current] + self.base_angle
                )
                # down strand
                domain[1].append(
                    domain[0][current+1] - 2.3
                )
            current += 1
        return self.theta_list

    def xs(self, count: int):
        """
        Generate x cords.

        Args:
            count (int): Number of x cords to generate.

        Returns:
            list: List of x cords in format [[[up strand], [down strand]], ...] for each domain.
        """
        current = 0
        while len(self.x_list[0][0]) < count:
            current += 1
            for domain_index, domain in enumerate(self.x_list):
                # up strand
                if self.thetas(count)[domain_index][0][current] < self.exterior_angles[domain_index]:
                    domain[0].append(
                        (self.thetas(count)[domain_index][0][current])
                        / self.exterior_angles[domain_index]
                    )
                else:
                    domain[0].append(
                        (360 - self.thetas(count)[domain_index][0][current])
                        / self.interior_angles[domain_index]
                    )
                # down strand
                print(self.thetas(count)[domain_index])
                print(self.thetas(count)[domain_index][1][current])
                if self.thetas[domain_index][1] < self.exterior_angles[domain_index]:
                    domain[1].append(
                        (self.thetas(count)[domain_index][1][current])
                        / self.exterior_angles[domain_index]
                    )
                else:
                    domain[1].append(
                        (360 - self.thetas(count)[domain_index][1][current])
                        / self.interior_angles[domain_index]
                    )

    def zs(self, count: int):
        """
        Generate z cords.

        Args:
            count (int): Number of z cords to generate.

        Returns:
            list: List of z cords in format [[[up strand], [down strand]], ...] for each domain.
        """
        while len(self.z_list[0][0]) < count:
            for domain in self.z_list:
                # up strand
                domain[0].append(domain[0][-1] + self.z_distance)
                # down strand
                domain[1].append(domain[0][-1] - self.switch_distance)
