import logging
from enum import Enum

from PyQt5.QtCore import QSize, pyqtSignal
from PyQt5.QtGui import QImage
from PyQt5.QtMultimedia import QCamera, QCameraImageCapture, QCameraViewfinderSettings
from PyQt5.QtMultimediaWidgets import QCameraViewfinder

logger = logging.getLogger(__name__)


class LiveFeedWidget(QCameraViewfinder):
    class _State(Enum):
        Init = "Init"
        Idle = "Idle"
        Preparing = "Preparing"
        WaitingForCapture = "WaitingForCapture"

    error = pyqtSignal(str)
    image_captured = pyqtSignal(QImage)

    def __init__(self, parent=None):
        super().__init__(parent)
        # Wouldn't it be great if python had lateinit
        self._requested_view_finder_resolution = None
        self._state = None
        self._camera: QCamera = None
        self._capture: QCameraImageCapture = None
        self._height_for_width: float = None

    def initialize(self, camera_info, requested_view_finder_resolution):
        self._requested_view_finder_resolution = _str_to_qsize(
            requested_view_finder_resolution
        )

        self._state = LiveFeedWidget._State.Init

        # Setup camera
        #
        self._camera = QCamera(camera_info)
        self._camera.setViewfinder(self)
        self._camera.setCaptureMode(QCamera.CaptureStillImage)
        self._camera.error.connect(self._on_camera_error)
        self._camera.statusChanged.connect(self._on_camera_status_changed)

        # Setup capture
        #
        self._capture = QCameraImageCapture(self._camera)
        self._capture.setCaptureDestination(QCameraImageCapture.CaptureToBuffer)
        self._capture.imageCaptured.connect(self._image_captured)
        self._capture.error.connect(self._on_capture_error)

        self._camera.start()

    def prepare(self):
        if self._state != LiveFeedWidget._State.Idle:
            logger.warning("Dropping call to prepare when in state: %s", self._state)
        else:
            self._state = LiveFeedWidget._State.Preparing
            self._camera.searchAndLock()

    def trigger_capture(self):
        if self._state != LiveFeedWidget._State.Preparing:
            logger.warning(
                "Dropping call to trigger_capture when in state: %s", self._state
            )
        else:
            logger.debug("trigger_capture")
            self._state = LiveFeedWidget._State.WaitingForCapture
            self._capture.capture()

    # noinspection PyPep8Naming
    def _on_camera_error(self, QCamera_Error: int):
        self._state = LiveFeedWidget._State.Idle
        self.error.emit(f"Camera error, code: {QCamera_Error}")

    # noinspection PyPep8Naming
    def _on_capture_error(self, p_int=None, QCameraImageCapture_Error=None, p_str=None):
        self._state = LiveFeedWidget._State.Idle
        self.error.emit(
            f"Capture error: {p_int} / {QCameraImageCapture_Error} / {p_str}"
        )

    def _image_captured(self, id_: int, image: QImage):
        if self._state != LiveFeedWidget._State.WaitingForCapture:
            logger.warning("Dropping _image_captured when in state: %s", self._state)
        self._state = LiveFeedWidget._State.Idle
        logger.debug("image captured: %s %s", id_, image)
        self._camera.unlock()
        self.image_captured.emit(image)

    def _on_camera_status_changed(self, status):
        logger.debug("_on_camera_status_changed: %s", status)
        if status == QCamera.LoadedStatus:
            supported_resolutions = self._camera.supportedViewfinderResolutions()
            logger.info("Supported view finder resolutions: %s", supported_resolutions)
            if self._requested_view_finder_resolution:
                if self._requested_view_finder_resolution in supported_resolutions:
                    logger.info(
                        "Setting resolution to %s",
                        self._requested_view_finder_resolution,
                    )
                    requested_settings = QCameraViewfinderSettings()
                    requested_settings.setResolution(
                        self._requested_view_finder_resolution
                    )
                    self._camera.setViewfinderSettings(requested_settings)
                else:
                    raise ValueError(
                        "Requested viewfinder resolution %s, "
                        "but the only supported resolutions are %s",
                        ", ".join(map(str, supported_resolutions)),
                    )

            camera_resolution = self._camera.viewfinderSettings().resolution()
            logger.info("Using resolution: %s", camera_resolution)
            self._height_for_width = (
                float(camera_resolution.height()) / camera_resolution.width()
            )

        if status == QCamera.ActiveStatus:
            self.show()
            self._state = LiveFeedWidget._State.Idle


def _str_to_qsize(val):
    (x, y) = val.split(",")
    return QSize(int(x), int(y))
