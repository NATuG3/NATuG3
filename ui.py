import pyqtgraph as pg
import numpy as np

# define the data
theTitle = "pyqtgraph plot"

if __name__ == '__main__':
    # create plot
    topView = pg.plot(x, y, title="Top View of DNA")
    topView.showGrid(x=True,y=True)
    topView.QtGui.QApplication.exec()