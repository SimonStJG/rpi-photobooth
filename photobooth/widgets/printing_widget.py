from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

from photobooth.state import Printing


class PrintingWidget(QLabel):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        # We want to be able to capture keyPress events here
        self.setFocusPolicy(Qt.StrongFocus)

        self.setText("Printing, please wait")

    def set_state(self, state: Printing):
        pass

