from PyQt6.QtWidgets import QPushButton


class StrandButton(QPushButton):
    def __init__(self, strand):
        super().__init__()

        if strand.strands.index(strand) is not None:
            self.setText(f"Strand #{strand.strands.index(strand) + 1}")
