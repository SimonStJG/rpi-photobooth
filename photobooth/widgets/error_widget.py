from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget

from photobooth.rpi_io import RpiIo, RpiIoQtHelper
from photobooth.uic import loadUi


class ErrorWidget(QWidget):
    accept = pyqtSignal()

    def __init__(self, rpi_io: RpiIo, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)

        self._io = RpiIoQtHelper(self, rpi_io)
        self._io.yes_button_pressed.connect(self.accept)
        self._io.no_button_pressed.connect(self.accept)

        loadUi("error.ui", self)

        self._errorMessage = self.findChild(QtWidgets.QLabel, "errorMessage")

    def set_message(self, message: str):
        self._errorMessage.setText(message)
