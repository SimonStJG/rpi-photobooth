import logging

from PyQt5.QtCore import QEvent, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage
from PyQt5.QtMultimedia import QCamera, QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QCameraViewfinder

logger = logging.getLogger(__name__)


class IdleWidget(QCameraViewfinder):
    image_captured = pyqtSignal(QImage)
    error = pyqtSignal(str)

    def __init__(self, camera_info, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.StrongFocus)

        self._camera = QCamera(camera_info)
        self._camera.setViewfinder(self)
        self._camera.setCaptureMode(QCamera.CaptureStillImage)
        self._camera.error.connect(self._on_camera_error)
        self._camera.start()

        self._capture = QCameraImageCapture(self._camera)
        self._capture.setCaptureDestination(QCameraImageCapture.CaptureToBuffer)

        self._capture.imageCaptured.connect(self._image_captured)
        self._capture.error.connect(self._on_capture_error)

        # TODO Should we wait for capture.captureAvailable() - what is this?

    def keyPressEvent(self, event: QEvent):
        super().keyPressEvent(event)

        key = event.key()
        logger.debug("keyPressEvent: %s", key)

        if key in [Qt.Key_Space, Qt.Key_Enter]:
            event.accept()
            self._capture.capture()
        else:
            event.ignore()

    @pyqtSlot
    def _image_captured(self, id_: int, image: QImage):
        logger.debug("imageCaptured: %s %s", id_, image)
        self.image_captured.emit(image)

    @pyqtSlot
    # noinspection PyPep8Naming
    def _on_camera_error(self, QCamera_Error: int):
        self.error.emit(f"Camera error, code: {QCamera_Error}")

    @pyqtSlot
    # noinspection PyPep8Naming
    def _on_capture_error(self, p_int=None, QCameraImageCapture_Error=None, p_str=None):
        self.error.emit(
            f"Capture error: {p_int} / {QCameraImageCapture_Error} / {p_str}"
        )
