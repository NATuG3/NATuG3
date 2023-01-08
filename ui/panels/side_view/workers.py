import logging
from functools import partial
from typing import List, Callable

import refs
import ui.dialogs.informers
import ui.plotters
import utils
from structures.domains import Domains
from structures.points import NEMid, Nucleoside
from structures.points.nick import Nick
from structures.points.point import Point
from structures.strands import Strands
from utils import inverse

logger = logging.getLogger(__name__)


def juncter(point: Point, strands: Strands, refresh: Callable) -> None:
    """
    Create a junction.

    Args:
        point: The point that was clicked.
        strands: A reference to all the strands currently plotted.
        refresh: Function called to refresh plot after juncter mode is run. This
            function does not always create junctions (for instance, if only one
            point is passed), so the function only calls refresh if a junction is
            created.
    """
    if isinstance(point, NEMid) and point.junctable:
        strands.conjunct(point, point.juncmate)
        refresh()
    else:
        raise ValueError("Point is not junctable.")
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
            logger.info(
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
    point.highlighted = inverse(point.highlighted)

    refresh()
    logger.info("Highlighter mode was run.")


def linker(point: Point, strands: Strands, refresh: Callable):
    """
    Create a linkage in a strand.

    Args:
        point: The points that the hairpin is being created for. linkages are
            recursively created for all points.
        strands: The strands object containing the points. The hairpin() method is
            called on this object.
        refresh: Function called to refresh plot after linker mode is run.
    """
    if not isinstance(point, NEMid):
        raise ValueError("Point is not a NEMid.")

    # Store the points that are currently selected
    currently_selected = refs.misc.currently_selected

    # If the point was already selected, deselect it
    if point.styles.is_state("selected"):
        point.styles.change_state("default")

    # Ensure that only endpoints are being selected
    NEMid_index = point.strand.items.by_type(NEMid).index(point)
    if (
        NEMid_index == 0
        or NEMid_index == len(point.strand.items.by_type(NEMid)) - 1
    ):
        currently_selected.append(point)
        point.styles.change_state("selected")
    else:
        utils.warning(
            refs.constructor,
            "Invalid Selection",
            "Linkages must be created across the ends of two strands. "
            "The point that was clicked on is not an end of a strand.",
        )

    # If two points are selected, create a linkage
    if len(currently_selected) == 2:
        strands.link(*currently_selected)
        currently_selected[0].styles.change_state("default")
        currently_selected[1].styles.change_state("default")
        currently_selected.clear()

    refresh()
    logger.info("Linkage mode was run.")
