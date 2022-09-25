def float_resizer(widget, limited_width, maximum_width=9999):
    """Adjust a dockable widget's size based on whether it is floating or not."""
    if widget.isFloating():
        widget.setMaximumWidth(maximum_width)
    else:
        widget.setMaximumWidth(limited_width)


def hide_or_unhide(widget):
    """
    Reverse the hiddenness of a widget
    """
    if widget.isHidden():
        widget.show()
    else:
        widget.hide()
