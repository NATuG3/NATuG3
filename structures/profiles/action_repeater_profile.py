from dataclasses import dataclass
from typing import Type, Tuple, Literal

from structures.points.nick import Nick
from structures.points.point import Point
from structures.strands import Strands


@dataclass
class ActionRepeaterProfile:
    """
    A profile that contains settings for repeating an action along a strand.

    Attributes:
        repeat_every: The number of nucleotides to skip between each action.
        repeat_for: The number of times to repeat the action. If None, repeat forever.
        bidirectional: Whether to repeat the action in both directions.
        types_to_run_on: The types of Point objects to run the action on.
        strands: The Strands container containing all strands that the bulk actions
            will be run on.
    """

    repeat_every: int
    repeat_for: int | None
    bidirectional: bool
    types_to_run_on: Tuple[Type, ...]
    strands: Strands

    def run(
        self,
        point: Point | Nick,
        action: Literal["nick", "unnick", "highlight", "conjunct"],
    ) -> None:
        """
        Run an action with the current settings along a strand beginning at a point.
        """
        self.strands.do_many(
            action,
            point,
            self.repeat_every,
            self.repeat_for,
            self.bidirectional,
            point.strand.by_type(self.types_to_run_on),
        )
