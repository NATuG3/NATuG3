from typing import Deque, Tuple, Type

# type annotation for the aforementioned container
DomainsContainerType: Type = Tuple[Tuple[Deque[float], Deque[float]], ...]

# container to store data for domains in
DomainsContainer = lambda count: tuple([[], []] for _ in range(count))
