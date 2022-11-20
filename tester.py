def main():
    import sys
    from PyQt6.QtWidgets import QApplication
    from ui.dialogs.sequence_editor import SequenceEditor

    app = QApplication(sys.argv)
    widget = SequenceEditor()
    widget.show()
    app.exec()
    sys.exit(app)


if __name__ == "__main__":
    main()