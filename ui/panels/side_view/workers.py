import ui.dialogs.informers
import ui.plotters
from structures.points import NEMid, Nucleoside
from structures.points.point import Point


class SidePointsClickedWorker:
    """
    The worker class for when a point is clicked on the side view plot.

    Attributes:
        points: The points that were clicked.
        plot: The plot containing the points.
    """

    def __init__(self, plot: ui.plotters.SideViewPlotter, points: list[Point]):
        self.plot = plot
        self.points = points

    def informer(self):
        """Run the informer mode."""

        # create a container for the dialog objects
        dialogs = []

        for point in self.points:
            # if a NEMid was clicked create a NEMidInformer object
            if isinstance(point, NEMid):
                dialogs.append(
                    ui.dialogs.informers.NEMidInformer(
                        self.parent(),
                        point,
                        self.strands,
                        self.domains,
                    )
                )
                # highlight the point that was clicked
                point.highlighted = True

            # if a Nucleoside was clicked create a NucleosideInformer objcet
            elif isinstance(point, Nucleoside):
                dialogs.append(
                    ui.dialogs.informers.NucleosideInformer(
                        self.parent(),
                        point,
                        self.strands,
                        self.domains,
                    )
                )
                # highlight the point that was clicked
                point.highlighted = True

        # if any dialogs were created then that means that points were highlighted
        # so we refresh the plot
        self.refresh()
