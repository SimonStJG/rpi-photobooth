from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QLabel

from photobooth.rpi_io import RpiIo, RpiIoQtHelper


class ErrorWidget(QLabel):
    accept = pyqtSignal()

    def __init__(self, rpi_io: RpiIo, parent=None, flags=Qt.WindowFlags()):
        super().__init___(self, parent, flags)
        self._io = RpiIoQtHelper(self, rpi_io)
        self._io.yes_button_pressed.connect(self.accept)
        self._io.no_button_pressed.connect(self.accept)

    def set_message(self, message: str):
        self.setText(message)
