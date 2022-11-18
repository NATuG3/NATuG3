import sys

from PyQt6.QtWidgets import QApplication

from ui.widgets import SequenceEditor

app = QApplication(sys.argv)
widget = SequenceEditor()
widget.show()
app.exec()
sys.exit(app)
