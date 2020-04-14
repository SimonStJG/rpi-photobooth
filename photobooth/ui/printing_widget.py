from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QLabel


class PrintingWidget(QLabel):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setText("Printing, please wait")

    def set_image(self, image: QImage):
        pass
