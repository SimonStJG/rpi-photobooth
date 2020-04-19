import logging
from enum import Enum

from PyQt5.QtCore import QEvent, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage
from PyQt5.QtMultimedia import QCamera, QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtWidgets import QGridLayout, QLabel, QWidget

from photobooth.rpi_io import RpiIo, RpiIoQtHelper
from photobooth.uic import load_ui
from photobooth.widgets.grid_layout_helper import set_grid_content_margins

logger = logging.getLogger(__name__)
COUNTDOWN_HEADER_DEFAULT_TEXT = "Press the green button"


class IdleWidget(QWidget):
    class State(Enum):
        Idle = "Idle"
        Countdown = "Countdown"
        AwaitingCapture = "AwaitingCapture"

    image_captured = pyqtSignal(QImage)
    error = pyqtSignal(str)

    def __init__(self, config, camera_info, rpi_io: RpiIo, parent=None):
        super().__init__(parent)
        self._countdown_timer_seconds = config.getint("countdownTimerSeconds")
        self._countdown_timer_seconds_remaining = None

        load_ui("idle.ui", self)
        set_grid_content_margins(self)
        self._countdown_header: QLabel = self.findChild(QLabel, "countdownHeader")
        self._countdown_header.setText(COUNTDOWN_HEADER_DEFAULT_TEXT)

        # Frustratingly, I couldn't work out how to add the QCameraViewfinder
        #  to the idle.ui file, so I am adding it manually
        # TODO Could try adding it to the photobooth.widgets package
        grid_layout = self.findChild(QGridLayout, "gridLayout")
        self._view_finder = QCameraViewfinder()
        grid_layout.addWidget(self._view_finder)

        # Setup camera
        #

        # TODO Ideally we would capture the viewfindersettings here and reduce
        #   the resolution so that the picture is smoother.  The docs suggest
        #   you call load() first, capture the state change, and read the settings
        #   then.  But when I do this gstreamer dies!

        # TODO Remove the horrible black box around the viewfinder

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

        # Countdown timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._countdown_timer_tick)

        # Setup RpiIo
        #
        self._io = RpiIoQtHelper(self, rpi_io)
        self._io.yes_button_pressed.connect(self._capture_requested)

        # Setup State
        #
        self.state = IdleWidget.State.Idle

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
        if self.state == IdleWidget.State.Idle:
            # This is a bit of a bodge, but the camera does usually become available
            #  pretty quickly
            self.state = IdleWidget.State.Countdown
            self._countdown_timer_seconds_remaining = self._countdown_timer_seconds
            self._countdown_header.setText(
                f"Get Ready: {self._countdown_timer_seconds_remaining}"
            )
            self._timer.start(1000)
        else:
            logger.warning("Dropping capture request when in state: %s", self.state)

    def _countdown_timer_tick(self):
        if self.state == IdleWidget.State.Idle:
            logger.warning("Dropping countdown tick while in idle state")
        else:
            self._countdown_timer_seconds_remaining -= 1
            # TODO De-dupe
            self._countdown_header.setText(
                f"Get Ready: {self._countdown_timer_seconds_remaining}"
            )
            logger.debug(
                "Countdown timer tick: %s", self._countdown_timer_seconds_remaining
            )
            if self._countdown_timer_seconds_remaining <= 0:
                self._timer.stop()
                self.state = IdleWidget.State.AwaitingCapture
                self._capture.capture()

    def _image_captured(self, id_: int, image: QImage):
        if self.state != IdleWidget.State.AwaitingCapture:
            logger.warning("Unexpected image captured while in state: %s", self.state)
        self.state = IdleWidget.State.Idle
        self._camera.unlock()
        self._countdown_header.setText(COUNTDOWN_HEADER_DEFAULT_TEXT)
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
