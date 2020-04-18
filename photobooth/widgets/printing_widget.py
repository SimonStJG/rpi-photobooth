from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QGridLayout

from photobooth.uic import loadUi
from photobooth.widgets.grid_layout_helper import set_grid_content_margins


class PrintingWidget(QWidget):
    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        loadUi("printing.ui", self)
        self._printingImage: QLabel = self.findChild(QLabel, "printingImage")
        set_grid_content_margins(self.findChild(QGridLayout, "gridLayout"))

    def set_image(self, image: QImage):
        self._printingImage.setPixmap(QPixmap().fromImage(image, Qt.AutoColor))
