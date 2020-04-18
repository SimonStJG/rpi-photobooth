import logging

from PyQt5.QtCore import QEvent, Qt, pyqtSignal
from PyQt5.QtGui import QImage
from PyQt5.QtMultimedia import QCamera, QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtWidgets import QGridLayout, QWidget

from photobooth.rpi_io import RpiIo, RpiIoQtHelper
from photobooth.uic import loadUi
from photobooth.widgets.grid_layout_helper import set_grid_content_margins

logger = logging.getLogger(__name__)


class IdleWidget(QWidget):
    image_captured = pyqtSignal(QImage)
    error = pyqtSignal(str)

    def __init__(self, camera_info, rpi_io: RpiIo, parent=None):
        super().__init__(parent)

        loadUi("idle.ui", self)

        grid_layout = self.findChild(QGridLayout, "gridLayout")
        set_grid_content_margins(grid_layout)

        # Frustratingly, I couldn't work out how to add the QCameraViewfinder
        #  to the idle.ui file, so I am adding it manually
        # TODO Could try adding it to the photobooth.widgets package
        self._view_finder = QCameraViewfinder()
        grid_layout.addWidget(self._view_finder)

        # Setup camera
        #
        self._camera = QCamera(camera_info)
        self._camera.setViewfinder(self._view_finder)
        self._camera.setCaptureMode(QCamera.CaptureStillImage)
        self._camera.error.connect(self._on_camera_error)
        self._camera.start()

        # Setup capture
        #
        self._capture = QCameraImageCapture(self._camera)
        self._capture.setCaptureDestination(QCameraImageCapture.CaptureToBuffer)
        self._capture.imageCaptured.connect(self._image_captured)
        self._capture.error.connect(self._on_capture_error)

        # Setup RpiIo
        #
        self._io = RpiIoQtHelper(self, rpi_io)
        self._io.yes_button_pressed.connect(self._capture_requested)

    def keyPressEvent(self, event: QEvent):
        super().keyPressEvent(event)

        key = event.key()
        logger.debug("keyPressEvent: %s", key)

        if key in [Qt.Key_Space, Qt.Key_Enter]:
            event.accept()
            self._capture_requested()
        else:
            event.ignore()

    def _capture_requested(self):
        # TODO (not very important) Could detect if the camera does not become
        #   available after a set period, or transitions from available to not
        #   available.
        if self._capture.isAvailable():
            self._capture.capture()
        else:
            logger.warning("Attempt to capture image before capture device ready")

    def _image_captured(self, id_: int, image: QImage):
        logger.debug("imageCaptured: %s %s", id_, image)
        self.image_captured.emit(image)

    # noinspection PyPep8Naming
    def _on_camera_error(self, QCamera_Error: int):
        self.error.emit(f"Camera error, code: {QCamera_Error}")

    # noinspection PyPep8Naming
    def _on_capture_error(self, p_int=None, QCameraImageCapture_Error=None, p_str=None):
        self.error.emit(
            f"Capture error: {p_int} / {QCameraImageCapture_Error} / {p_str}"
        )
