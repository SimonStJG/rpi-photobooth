import logging

from PyQt5.QtCore import QEvent, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel

from photobooth.rpi_io import RpiIo, RpiIoQtHelper

logger = logging.getLogger(__name__)


class PreviewWidget(QLabel):
    accept = pyqtSignal()
    reject = pyqtSignal()

    def __init__(self, rpi_io: RpiIo, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.setFocusPolicy(Qt.StrongFocus)
        self._io = RpiIoQtHelper(self, rpi_io)
        self._io.yes_button_pressed.connect(self.accept)
        self._io.no_button_pressed.connect(self.reject)

    def set_image(self, image: QImage):
        self.setPixmap(QPixmap().fromImage(image, Qt.AutoColor))

    def keyPressEvent(self, event: QEvent):
        super().keyPressEvent(event)

        key = event.key()
        logger.debug("keyPressEvent: %s", key)

        if key == Qt.Key_Space:
            event.accept()
            self.accept.emit()
        elif key == Qt.Key_Escape:
            event.accept()
            self.reject.emit()
        else:
            event.ignore()
