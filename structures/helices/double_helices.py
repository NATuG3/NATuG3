from typing import List

from structures.domains import Domain
from structures.helices import DoubleHelix


class DoubleHelices:
    """
    A container for many DoubleHelix objects.

    This class provides methods to automatically determining matching items,
    set junctability, and more.

    Attributes:
        double_helices (list): A list of DoubleHelix objects.
    """

    __slots__ = "double_helices"

    def __init__(
        self, double_helices: List[DoubleHelix] = None, domains: List[Domain] = None
    ) -> None:
        """
        Create a double helices container.

        Args:
            double_helices: A list of DoubleHelix objects.
            domains: A list of domains to assign to the double helices. This should
                not be provided if double_helices is provided. If this is provided, the
                double helices will be automatically created.
        """
        self.double_helices = double_helices or [
            DoubleHelix(domain) for domain in domains
        ]

    def __len__(self) -> int:
        return len(self.double_helices)

    def __getitem__(self, index: int) -> DoubleHelix:
        return self.double_helices[index]

    def domains(self) -> List[Domain]:
        """
        Obtain all the domains of all the double helices in their respective order.

        Returns:
            A list of all the domains.
        """
        return [double_helix.domain for double_helix in self.double_helices]

    def assign_junctability(self) -> None:
        """
        Assign juncmates and junctability for all NEMids contained in all helices.
        """
        # Iterate through all the double helices
        for index, double_helix in enumerate(self.double_helices):
            # To determine the next zeroed strand's direction we either look at the next
            # strand's zeroed strand, or we wrap back to the first domain if we have
            # reached the last domain (since cross-screen junctions are perfectly
            # acceptable.
            if index != len(self.domains()) - 1:
                next_strand_index = index + 1
            else:
                next_strand_index = 0

            # The zeroed strand directions for the current and next strand
            current_zeroed_strand_direction = domains[domain.index].left_helix_joint
            next_zeroed_strand_direction = domains[next_strand_index].left_helix_joint

            # The actual current domain's strands and the next domain's strands. Note
            # that "strand_pair" here means that it is a tuple of two strands,
            # one being up, and the other being down.
            current_zeroed_strand = strands[domain.index][
                current_zeroed_strand_direction
            ]
            next_zeroed_strand = strands[next_strand_index][
                next_zeroed_strand_direction
            ]

            for item1 in current_zeroed_strand.items:
                for item2 in next_zeroed_strand.items:

                    def junct():
                        """Assign junctability and juncmates to the items."""
                        # Set junctability
                        item1.junctable = True
                        item2.junctable = True

                        # Set juncmates
                        item1.juncmate = item2
                        item2.juncmate = item1

                    # Perform a preliminary z coord check since dist() is much more
                    # computationally intensive, and it is best to avoid it if possible
                    if abs(item1.z_coord - item2.z_coord) > settings.junction_threshold:
                        continue
                    elif (x_dist := abs(item1.x_coord - item2.x_coord)) > len(
                        domains
                    ) - 0.1 and self.closed():
                        junct()
                    elif x_dist < settings.junction_threshold:
                        junct()
