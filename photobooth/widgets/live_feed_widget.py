import logging
from enum import Enum

from PyQt5.QtCore import QSizeF, Qt, pyqtSignal
from PyQt5.QtGui import QImage, QPainter, QPixmap, QTransform
from PyQt5.QtMultimedia import QCamera, QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtWidgets import QGraphicsView

from photobooth.camera import Camera
from photobooth.mask import Mask
from photobooth.widgets.overlay_text_graphics_scene import OverlayTextGraphicsScene

logger = logging.getLogger(__name__)


class LiveFeedWidget(QGraphicsView):
    class _State(Enum):
        Init = "Init"
        Idle = "Idle"
        Preparing = "Preparing"
        WaitingForCapture = "WaitingForCapture"

    error = pyqtSignal(str)
    image_captured = pyqtSignal(QImage)
    initialized = pyqtSignal()

    def __init__(
        self, camera: Camera, is_mirrored: bool, mask: Mask, parent=None,
    ):
        super().__init__(parent=parent)
        self._is_mirrored = is_mirrored
        self._mask = mask

        self._state = LiveFeedWidget._State.Init

        self._video_item = QGraphicsVideoItem()
        # I think this is the size in pixels on the screen?
        self._video_item.setSize(QSizeF(self._mask.size))
        # TODO I think this will not draw centrally?  If not should fix this
        self._video_item.setAspectRatioMode(Qt.KeepAspectRatioByExpanding)
        if self._is_mirrored:
            self._video_item.setTransform(QTransform().scale(-1, 1))

        self.setMask(self._mask.clip_region)

        self._scene: OverlayTextGraphicsScene = OverlayTextGraphicsScene(
            self._mask.size
        )
        self._scene.addItem(self._video_item)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setScene(self._scene)

        # Setup camera
        #
        self._camera = camera
        self._camera.setViewfinder(self._video_item)
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

        logger.info("Camera started")

    def set_overlay_text(self, text: str):
        self._scene.set_overlay_text(text)

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

        # TODO If I don't unload and the reload the camera, gstreamer dies
        #  with CameraBin error: "Internal data stream error.", not sure why
        #  :(
        self._camera.unload()

        self.image_captured.emit(_mirror_if_necessary(image, self._is_mirrored))

    def reload(self):
        # See comment on _image_captured
        self._camera.start()

    def _on_camera_status_changed(self, status):
        logger.debug("_on_camera_status_changed: %s", status)
        if status == QCamera.ActiveStatus:
            self._state = LiveFeedWidget._State.Idle
            self.initialized.emit()


def _mirror_if_necessary(image, is_mirrored):
    if not is_mirrored:
        return image

    mirrored = QImage(image.size(), QImage.Format_RGB32)

    painter = QPainter(mirrored)
    painter.setRenderHints(QPainter.Antialiasing, QPainter.SmoothPixmapTransform)
    pixmap = QPixmap.fromImage(image)
    if is_mirrored:
        pixmap = pixmap.transformed(QTransform().scale(-1.0, 1.0))
    painter.drawPixmap(0, 0, pixmap)
    painter.end()

    return mirrored
