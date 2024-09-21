from dataclasses import dataclass
from typing import Literal

from natug.structures.points.nick import Nick
from natug.structures.points.point import Point
from natug.structures.strands import Strands


@dataclass
class ActionRepeaterProfile:
    """
    A profile that contains settings for repeating an action along a strand.

    Attributes:
        repeat_every: The number of nucleotides to skip between each action.
        repeat_every_multiplier: The multiplier to apply to the repeat_every value.
        repeat_for: The number of times to repeat the action. If None, repeat forever.
        bidirectional: Whether to repeat the action in both directions.
        strands: The Strands container containing all strands that the bulk actions
            will be run on.
    """

    repeat_every: int
    repeat_every_multiplier: int
    repeat_for: int | None
    bidirectional: bool
    strands: Strands

    def run(
        self,
        point: Point | Nick,
        action: Literal["nick", "unnick", "highlight", "conjunct"],
    ) -> None:
        """
        Run an action with the current settings along a helix beginning at a point.

        Args:
            point: The point to start the action at. Must have a "helix" attribute.
            action: The action to run.
        """
        self.strands.do_many(
            action,
            point,
            self.repeat_every * self.repeat_every_multiplier,
            self.repeat_for,
            self.bidirectional,
            point.helix.data.points,
        )
