import logging

from PyQt5.QtCore import Qt, pyqtSignal, QEvent
from PyQt5.QtGui import QImage
from PyQt5.QtMultimedia import QCamera, QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QCameraViewfinder

logger = logging.getLogger(__name__)


class IdleWidget(QCameraViewfinder):
    # TODO Is this really right, or does it only work b/c this is a singleton?
    imageCaptured = pyqtSignal(QImage)

    def __init__(self, camera_info, parent=None):
        super().__init__(parent)
        # We want to be able to capture keyPress events here
        self.setFocusPolicy(Qt.StrongFocus)

        self.camera = QCamera(camera_info)
        self.camera.setViewfinder(self)
        self.camera.setCaptureMode(QCamera.CaptureStillImage)
        self.camera.start()

        self.capture = QCameraImageCapture(self.camera)
        self.capture.setCaptureDestination(QCameraImageCapture.CaptureToBuffer)

        self.capture.imageCaptured.connect(self._image_captured)

        # TODO Should we wait for capture.captureAvailable() - what is this?
        # TODO There is an error signal - should handle it

    def keyPressEvent(self, event: QEvent):
        super().keyPressEvent(event)

        key = event.key()
        logger.debug("keyPressEvent: %s", key)

        if key in [Qt.Key_Space, Qt.Key_Enter]:
            event.accept()
            self.capture.capture()
        else:
            event.ignore()

    def _image_captured(self, id_: int, image: QImage):
        logger.debug("imageCaptured: %s %s", id_, image)
        self.imageCaptured.emit(image)
