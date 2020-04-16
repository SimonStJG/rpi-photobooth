import logging

from PyQt5.QtCore import QEvent, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QLabel

logger = logging.getLogger(__name__)


class PreviewWidget(QLabel):
    accept = pyqtSignal()
    reject = pyqtSignal()

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        self.setFocusPolicy(Qt.StrongFocus)

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
