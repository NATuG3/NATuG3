import sys
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
)
import dna_nanotube_tools.plot

class mainWindow(QMainWindow):
    def __init__(self):
        # this is an inherented class of QMainWindow
        # so we must initialize the parent qt widget
        super().__init__()
        # this activates the parent's __init__()

        # configure the main window's general settings
        # initilize a main widget/layout
        self.central_widget = (
            QWidget()
        )  # this is the main widget, which is just a layout
        self.central_layout = (
            QVBoxLayout()
        )  # this is the main layout, which the central widget is a frame for

        # utilize inhereted methods to set up the main window
        self.setWindowTitle("DNA Constructor")
        self.setCentralWidget(self.central_widget)
        self.centralWidget().setLayout(
            self.central_layout
        )  # this is an inhereted method

        # add dna previews on top
        self.central_layout.addWidget(self._generate_dna_previews())
        # configuration panel on bottom
        self.central_layout.addWidget(QLabel("Placeholder for configuration panel"))


    def _generate_dna_previews(self) -> QWidget:
        """Generate a QWidget of the two dna previews side by side."""
        # define domains to generate sideview for
        domains = [dna_nanotube_tools.domain(9, 0)] * 14

        # initilize side view class
        side_view = dna_nanotube_tools.plot.side_view(domains, 3.38, 12.6, 2.3)
        top_view = dna_nanotube_tools.plot.top_view(domains, 2.2)

        # the dna previews will be a side by side array of widgets
        dna_previews = QHBoxLayout()
        dna_previews.addWidget(side_view.ui(150))
        dna_previews.addWidget(top_view.ui())

        # convert the above dna_previews layout into an actual widget
        widgetized_output = QWidget()
        widgetized_output.setLayout(dna_previews)
        widgetized_output.show()

        # return the output as a widget
        return widgetized_output


# this ensures that the program is being run directly (since this is indeeed the main file)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = mainWindow()
    window.show()
    sys.exit(app.exec())
