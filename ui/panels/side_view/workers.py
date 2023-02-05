import logging
from functools import partial
from typing import Callable

from PyQt6.QtWidgets import QMainWindow

import ui.dialogs.informers
import ui.plotters
import utils
from structures.domains import Domains
from structures.points import NEMid, Nucleoside
from structures.points.nick import Nick
from structures.points.point import Point
from structures.strands import Strands

logger = logging.getLogger(__name__)


def juncter(
    point: Point,
    strands: Strands,
    refresh: Callable,
    runner: "runner.Runner",
    error_title="Invalid Point Clicked",
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
    """
    if isinstance(point, NEMid) and point.junctable:
        strands.conjunct(point, point.juncmate)
        refresh()
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
    parent, point: Point, strands: Strands, domains: Domains, refresh: Callable
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
                ui.dialogs.informers.NEMidInformer(
                    parent,
                    point,
                    strands,
                    domains,
                )
            )
            # highlight the point that was clicked
            point.styles.change_state("highlighted")

        # if a Nucleoside was clicked create a NucleosideInformer objcet
        elif isinstance(point, Nucleoside):
            dialogs.append(
                ui.dialogs.informers.NucleosideInformer(
                    parent,
                    point,
                    strands,
                    domains,
                )
            )
            # highlight the point that was clicked
            point.styles.change_state("highlighted")

        # if an unsupported type of point is clicked raise an error
        else:
            logger.warn(
                "Unsupported point type passed to informer. Point type: %s", type(point)
            )

    def dialog_complete(dialogs_, points_):
        """Worker function to be called when all dialogs are closed."""
        for dialog_ in dialogs_:
            dialog_.close()
        for point_ in points_:
            point_.styles.change_state("default")

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


def nicker(point: Point, strands: Strands, refresh: Callable) -> None:
    """
    Create a nick in a strand, or undoes a nick.

    Args:
        point: The points that the nick is being created/removed for. Nicks are
            recursively created for all points.
        strands: The strands object containing the points. The nick() method is called
            on this object.
        refresh: Function called to refresh plot after nicker mode is run.
    """
    if isinstance(point, Nick):
        strands.unnick(point)
    else:
        strands.nick(point)

    refresh()
    logger.info("Nicker mode was run.")


def highlighter(point: Point, refresh: Callable):
    """
    Highlight/un-highlight a series of points based on their current highlighted state.

    Args:
        point: The point to highlight.
        refresh: Function called to refresh plot after highlighter mode is run.
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
    # Ensure that only endpoints are being selected
    if not point.is_endpoint(of_its_type=True):
        print(point.is_endpoint(of_its_type=True))
        print(point.strand.index(point))
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
    currently_selected = runner.misc.currently_selected

    # At this point the point should be guaranteed to be a NEMid
    assert isinstance(point, NEMid)

    # If the point was already selected, deselect it.
    if point.styles.is_state("selected"):
        currently_selected.remove(point)
        point.styles.change_state("default")
    # If a point is already selected, create a linkage between the previously selected
    # point and the currently selected point.
    elif len(currently_selected) == 1:
        # Ensure that the direction of the point that we are about to make a linkage
        # for is different to the direction of the point that is already selected.
        if currently_selected[0].direction == point.direction:
            logger.warning(
                "User tried to create a linkage with two points in the same direction."
            )
            utils.warning(
                runner.window,
                error_title,
                "Linkages must be created across NEMids of differing directions. The "
                "selected NEMids are not of differing directions.",
            )
            return

        strands.link(currently_selected[0], point)
        currently_selected[0].styles.change_state("default")
        point.styles.change_state("default")
        currently_selected.clear()
    # If no points are already selected, select the point.
    elif len(currently_selected) == 0:
        currently_selected.append(point)
        point.styles.change_state("selected")

    refresh()
    logger.info("Linkage mode was run.")
