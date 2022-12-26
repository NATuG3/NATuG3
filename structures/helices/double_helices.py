from typing import List

import settings


class DoubleHelices:
    """
    A container for many DoubleHelix objects.

    This class provides methods to automatically determining matching items,
    set junctability, and more.

    Attributes:
        double_helices (list): A list of DoubleHelix objects.
    """

    __slots__ = "double_helices"

    def __init__(self, items: List["Domain"] | List["DoubleHelix"]) -> None:
        """
        Create a double helices container.

        Args:
            items: Either a list of domains or a list of double helices. If it is a
                list of domains then the double helices will be automatically created.
        """
        from structures.domains import Domain
        from structures.helices import DoubleHelix

        if isinstance(items[0], Domain):
            self.double_helices = [DoubleHelix(domain) for domain in items]
        else:
            self.double_helices = items

    def __len__(self) -> int:
        return len(self.double_helices)

    def __getitem__(self, index: int) -> "DoubleHelix":
        return self.double_helices[index]

    def domains(self) -> List["Domain"]:
        """
        Obtain all the domains of all the double helices in their respective order.

        Returns:
            A list of all the domains.
        """
        return [double_helix.domain for double_helix in self.double_helices]

    def assign_junctability(self, closed: bool = True) -> None:
        """
        Assign juncmates and junctability for all NEMids contained in all helices.

        Args:
            closed: Whether to assume the tube is closed or not.
        """
        # Create a list of all the domains
        domains = self.domains()

        # Iterate through all the double helices
        for index, double_helix in enumerate(self.double_helices):
            # The actual current domain's strands and the next domain's strands. Note
            # that "strand_pair" here means that it is a tuple of two strands,
            # one being up, and the other being down.
            current_zeroed_strand = double_helix.zeroed_helix
            next_zeroed_strand = self.double_helices[
                index + 1 if index + 1 != len(domains) else 0
            ].zeroed_helix

            for item1 in current_zeroed_strand.NEMids():
                for item2 in next_zeroed_strand.NEMids():
                    # Create a function that will assign the juncmate and junctability
                    # of the two NEMids if they need to be assigned.
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
                    ) - 0.1 and closed:
                        junct()
                    elif x_dist < settings.junction_threshold:
                        junct()
