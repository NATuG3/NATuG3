
# create PyQtGraph widget
ui_widget = pg.plot(
    us,
    vs,
    title="Top View of DNA",
    symbol="o",
    symbolSize=80,
    pxMode=True,
)
ui_widget.setAspectLocked(lock=True, ratio=1)
ui_widget.showGrid(x=True, y=True)