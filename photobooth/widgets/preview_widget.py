import logging

from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel

from photobooth.state import Preview

logger = logging.getLogger(__name__)


class PreviewWidget(QLabel):
    accept = pyqtSignal()
    reject = pyqtSignal()

    def __init__(self, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)
        # We want to be able to capture keyPress events here
        self.setFocusPolicy(Qt.StrongFocus)

    def set_state(self, state: Preview):
        self.setPixmap(QPixmap().fromImage(state.image, Qt.AutoColor))

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
