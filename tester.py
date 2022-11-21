import sys

from PyQt6.QtWidgets import QApplication

from ui.dialogs.sequence_editor.sequence_editor import SequenceEditor


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    widget = SequenceEditor()
    widget.show()
    app.exec()
    sys.exit(app)


if __name__ == "__main__":
    main()
