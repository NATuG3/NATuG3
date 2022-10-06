from PyQt6.QtWidgets import QMessageBox


def yes_no_prompt(parent, title, msg):
    choice = QMessageBox.question(
        parent,
        title,
        msg,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    if choice == QMessageBox.StandardButton.Yes:
        return True
    else:
        return False
