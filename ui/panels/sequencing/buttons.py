from PyQt6.QtWidgets import QPushButton


class StrandButton(QPushButton):
    def __init__(self, strand):
        super().__init__()

        if strand.parent.index(strand) is not None:
            self.setText(f"Strand #{strand.parent.index(strand) + 1}")
