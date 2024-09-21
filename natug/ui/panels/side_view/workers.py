import logging
from contextlib import suppress
from functools import partial
from typing import Callable

from natug import utils
from natug.structures.domains import Domains
from natug.structures.points import NEMid, Nucleoside
from natug.structures.points.nick import Nick
from natug.structures.points.point import Point
from natug.structures.profiles.action_repeater_profile import \
    ActionRepeaterProfile
from natug.structures.strands import Strands
from natug.structures.strands.linkage import Linkage
from natug.ui.dialogs import informers

logger = logging.getLogger(__name__)


def juncter(
    point: Point,
    strands: Strands,
    refresh: Callable,
    runner: "runner.Runner",
    repeat: ActionRepeaterProfile | None,
    error_title: str = "Invalid Point Clicked",
) -> None:
    """
    Create a junction.

    Args:
        point: The point that was clicked.
        strands: A reference to all the strands currently plotted.
        refresh: Function called to refresh plot after juncter mode is run. This
            function does not always create junctions (for instance, if only one
            point is passed), so the function only calls refresh if a junction is
            created.
        runner: NATuG's runner.
        error_title: The title of the error dialog that is shown when the user clicks
            an invalid point.
        repeat: The action repeater profile to use for repeating the action, or None
            to not repeat the action.
    """
    if isinstance(point, NEMid) and point.junctable:
        if repeat:
            repeat.run(point, "conjunct")
        else:
            if not bool(point.juncmate) or not bool(point.juncmate.strand):
                utils.warning(
                    runner.window,
                    "NEMid Juncmate not found",
                    "The NEMid that was clicked did not have a juncmate and thus a"
                    "junction could not be created. This is likely because the juncmate"
                    "is currently nicked out.",
                )
                return
            strands.conjunct(point, point.juncmate)
        refresh()
        runner.snapshot()
    else:
        utils.warning(
            runner.window,
            error_title,
            "Junctions can only be created by clicking on overlapping NEMids. "
            "Junctable NEMids are made white, and are overlapping.\n\n"
            "The point clicked was either not an overlapping NEMid, or was not a NEMid "
            "at all.",
        )
    logger.info("Juncter mode was run.")


def informer(
    parent,
    point: Point,
    strands: Strands,
    domains: Domains,
    refresh: Callable,
) -> None:
    """
    Create an informer for a clicked point and its juncmate (if applicable).

    Args:
        parent: The strands widget. This is what all dialogs will be parented to.
        point: The points that the informer is being created for.
        strands: A reference to all the strands currently plotted.
        domains: A reference to all the domains currently plotted.
        refresh: Function called to refresh plot after informer mode is run. This is
            necessary because the informer mode may not change the plot, so simply
            always refreshing the plot is a inefficient.

    Notes:
        If a point that is not a Nucleoside or NEMid is passed then the function does
        nothing.
    """

    # create a container for the dialog objects
    dialogs = []

    if isinstance(point, NEMid) and point.junctable:
        points = [point, point.juncmate]
    else:
        points = [point]

    for point in points:
        # if a NEMid was clicked create a NEMidInformer object
        if isinstance(point, NEMid):
            dialogs.append(
                informers.NEMidInformer(
                    parent,
                    point,
                    strands,
                    domains,
                )
            )
            # highlight the point that was clicked
            point.styles.change_state("highlighted")

        # if a Nucleoside was clicked create a NucleosideInformer object
        elif isinstance(point, Nucleoside):
            dialogs.append(
                informers.NucleosideInformer(
                    parent,
                    point,
                    strands,
                    domains,
                )
            )
            # highlight the point that was clicked
            point.styles.change_state("highlighted")
            if point.matching is not None:
                point.matching.styles.change_state("highlighted")

        # if an unsupported type of point is clicked raise an error
        else:
            logger.warning(
                "Unsupported point type passed to informer. Point type: %s", type(point)
            )

    def dialog_complete(dialogs_, points_) -> None:
        """Worker function to be called when all dialogs are closed."""
        for dialog_ in dialogs_:
            dialog_.close()
        for point_ in points_:
            point_.styles.change_state("default")
            if isinstance(point_, Nucleoside) and point_.matching is not None:
                point_.matching.styles.change_state("default")

    if len(dialogs) > 0:
        # connect the completed events for all the dialogs
        wrapped_dialog_complete = partial(dialog_complete, dialogs, points)

        # so that the dialogs aren't all on top of one another we will shift each one
        # 5 pixels down and to the right from the previous one for each dialog (so
        # that the user can see that there are multiple dialogs)
        shift = 0
        for dialog in dialogs:
            # connect the completed event
            dialog.finished.connect(wrapped_dialog_complete)

            # show the dialog
            dialog.show()

            # shift the dialog
            dialog.move(dialog.x() + shift, dialog.y() + shift)
            shift += 10

        # refresh upon last dialog being closed
        dialogs[-1].finished.connect(refresh)

        # refresh the plot
        refresh()

    logger.info("Informer mode was run.")


def nicker(
    point: Point,
    strands: Strands,
    runner: "Runner",
    refresh: Callable,
    repeat: ActionRepeaterProfile,
) -> None:
    """
    Create a nick in a strand, or undoes a nick.

    Args:
        point: The points that the nick is being created/removed for. Nicks are
            recursively created for all points.
        strands: The strands object containing the points. The nick() method is called
            on this object.
        runner: NATuG's runner.
        refresh: Function called to refresh plot after nicker mode is run.
        repeat: The action repeater profile to use for repeating the action, or None
            to not repeat the action.
    """
    if isinstance(point, Nick):
        if repeat:
            repeat.run(point, "unnick")
        else:
            strands.unnick(point)
    else:
        if repeat:
            repeat.run(point, "nick")
        else:
            if isinstance(point, NEMid) and point.junction:
                utils.warning(
                    runner.window,
                    "Active Junction Nicking",
                    "You cannot nick out one of the two points of an active junction "
                    "site.",
                )
                return
            with suppress(IndexError):
                if isinstance(
                    potential_linkage := point.surf_strand(2), Linkage
                ) or isinstance(potential_linkage := point.surf_strand(-2), Linkage):
                    strands.unlink(potential_linkage)

            strands.nick(point)

    runner.snapshot()
    refresh()
    logger.info("Nicker mode was run.")


def highlighter(
    point: Point,
    refresh: Callable,
    repeat: bool,
) -> None:
    """
    Highlight/un-highlight a series of points based on their current highlighted state.

    Args:
        point: The point to highlight.
        refresh: Function called to refresh plot after highlighter mode is run.
        repeat: The action repeater profile to use for repeating the action, or None
            to not repeat the action.
    """
    if point.styles.state == "highlighted":
        point.styles.change_state("default")
    else:
        point.styles.change_state("highlighted")

    refresh()
    logger.info("Highlighter mode was run.")


def linker(
    point: Point,
    strands: Strands,
    refresh: Callable,
    runner: "runner.Runner",
    error_title="Invalid Selection",
):
    """
    Create a linkage in a strand.

    Args:
        point: The points that the hairpin is being created for. linkages are
            recursively created for all points.
        strands: The strands object containing the points. The hairpin() method is
            called on this object.
        refresh: Function called to refresh plot after linker mode is run.
        runner: NATuG's runner.
        error_title: The title of the error dialog that is shown if the user tries to
            create an invalid linkage. Defaults to "Invalid Selection".
    """
    # Ensure that the point is a NEMid
    if isinstance(point, Nick):
        utils.warning(
            runner.window,
            error_title,
            "Linker mode only works on NEMids. A nick was clicked. To undo a nick "
            "please enter nicker mode.",
        )
        return
    elif not isinstance(point, NEMid):
        utils.warning(
            runner.window,
            error_title,
            "Linker mode only works on NEMids. Please click on a NEMid to begin "
            "creating a linkage.",
        )
        return
    # Ensure that only endpoints are being selected
    if not point.is_endpoint(of_its_type=True):
        logger.warning("User tried to create a linkage on a non-endpoint.")
        utils.warning(
            runner.window,
            error_title,
            "Linkages must be created across the ends of two strands. "
            "The point that was clicked on is not an end of a strand.",
        )
        return
    # Ensure that the strand that is having an item selected contains at least two
    # items.
    if len(point.strand) < 2:
        logger.warning("User tried to create a linkage on a strand with only one item.")
        utils.warning(
            runner.window,
            error_title,
            "Linkages must be created across the ends of two strands. "
            "The strand that was clicked on only contains one item.",
        )
        return

    # Store the points that are currently selected
    currently_selected = runner.managers.misc.currently_selected

    # If the point was already selected, deselect it.
    if point.styles.is_state("selected"):
        currently_selected.remove(point)
        point.styles.change_state("default")

    # If a point is already selected, create a linkage between the previously selected
    # point and the currently selected point.
    elif len(currently_selected) == 1:
        point1 = point
        point2 = currently_selected[0]

        if (point1.is_head(1) and point2.is_tail(1)) or (
            point1.is_tail(1) and point2.is_head(1)
        ):
            strands.link(point1, point2)
            currently_selected[0].styles.change_state("default")
            point.styles.change_state("default")
            currently_selected.clear()
            runner.snapshot()
        else:
            utils.warning(
                runner.window,
                error_title,
                "Linkages must be created across the head of one strand to the tail "
                "of another strand.",
            )

    # If no points are already selected, select the point.
    elif len(currently_selected) == 0:
        currently_selected.append(point)
        point.styles.change_state("selected")

    refresh()
    logger.info("Linkage mode was run.")
