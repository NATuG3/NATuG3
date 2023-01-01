import logging
from functools import partial
from typing import List, Callable

import ui.dialogs.informers
import ui.plotters
from structures.domains import Domains
from structures.points import NEMid, Nucleoside
from structures.points.nick import Nick
from structures.points.point import Point
from structures.strands import Strands
from utils import inverse

logger = logging.getLogger(__name__)


def juncter(points: List[NEMid], strands: Strands, refresh: Callable) -> None:
    """
    Create a junction.

    Args:
        points: The points that the junction is being created for.
        strands: A reference to all the strands currently plotted.
        refresh: Function called to refresh plot after juncter mode is run. This function does not always create
            junctions (for instance, if only one point is passed), so the function only calls refresh if a junction
            is created.

    Notes:
        If more or less than two points or passed, or if either point is not a NEMid, the function does nothing.
    """
    if len(points) == 2:
        if all([isinstance(item, NEMid) for item in points]):
            strands.conjunct(points[0], points[1])
            refresh()
        else:
            raise TypeError(
                "Both points must be NEMids to create a junction. Types passed: %s and %s. Ignoring request.",
                type(points[0]),
                type(points[1]),
            )
    else:
        logger.debug(
            "Two points needed to create a junction; however, %s were passed. Ignoring request.",
            len(points),
        )
    logger.info("Juncter mode was run.")


def informer(
    parent, points: List[Point], strands: Strands, domains: Domains, refresh: Callable
) -> None:
    """
    Create an informer for a clicked point and its juncmate (if applicable).

    Args:
        parent: The parent widget. This is what all dialogs will be parented to.
        points: The points that the informer is being created for.
        strands: A reference to all the strands currently plotted.
        domains: A reference to all the domains currently plotted.
        refresh: Function called to refresh plot after informer mode is run. This is necessary because the informer
            mode may not change the plot, so simply always refreshing the plot is a inefficient.

    Notes:
        If a point that is not a Nucleoside or NEMid is passed then the function does nothing.
    """

    # create a container for the dialog objects
    dialogs = []

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
            point.highlighted = True

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
            point.highlighted = True

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
            point_.highlighted = False

    if len(dialogs) > 0:
        # connect the completed events for all the dialogs
        wrapped_dialog_complete = partial(dialog_complete, dialogs, points)

        # so that the dialogs aren't all on top of one another we will shift each one 5 pixels down and to the right
        # from the previous one for each dialog (so that the user can see that there are multiple dialogs)
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


def nicker(points: List[Point], strands: Strands, refresh: Callable) -> None:
    """
    Create a nick in a strand, or undoes a nick.

    Args:
        points: The points that the nick is being created/removed for. Nicks are
            recursively created for all points.
        strands: The strands object containing the points. The nick() method is called
            on this object.
        refresh: Function called to refresh plot after nicker mode is run.
    """
    for point in points:
        if isinstance(point, Nick):
            strands.unnick(point)
        else:
            strands.nick(point)

    refresh()
    logger.info("Nicker mode was run.")


def highlighter(points: List[Point], refresh: Callable):
    """
    Highlight/un-highlight a series of points based on their current highlighted state.

    Args:
        points: The points to highlight.
        refresh: Function called to refresh plot after highlighter mode is run.
    """
    for point in points:
        point.highlighted = inverse(point.highlighted)

    refresh()
    logger.info("Highlighter mode was run.")


def hairpinner(points: List[Point], strands: Strands, refresh: Callable):
    """
    Create a hairpin in a strand.

    Args:
        points: The points that the hairpin is being created for. Hairpins are
            recursively created for all points.
        strands: The strands object containing the points. The hairpin() method is called
            on this object.
        refresh: Function called to refresh plot after hairpinner mode is run.
    """
    if len(points) == 2:
        strands.conjunct(points[0], points[1])
    elif len(points) == 1:
        selected_points = tuple(filter(lambda point: point.selected, strands.points()))
        if len(selected_points) == 1:

            strands.connect(points[0], selected_points[0])
            selected_points[0].selected = False
        else:
            points[0].selected = True

    refresh()
    logger.info("Hairpinner mode was run.")
