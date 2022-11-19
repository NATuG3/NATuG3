import sys

from PyQt6.QtWidgets import QApplication

from ui.widgets.sequence_editor.sequence_editor import SequenceEditor

app = QApplication(sys.argv)
widget = SequenceEditor()
widget.show()
app.exec()
sys.exit(app)
