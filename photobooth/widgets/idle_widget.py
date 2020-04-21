import logging
from enum import Enum

from PyQt5.QtCore import QEvent, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage
from PyQt5.QtWidgets import QLabel, QWidget

from photobooth.rpi_io import RpiIo, RpiIoQtHelper
from photobooth.uic import load_ui
from photobooth.widgets.grid_layout_helper import set_grid_content_margins
from photobooth.widgets.live_feed_widget import LiveFeedWidget

logger = logging.getLogger(__name__)
COUNTDOWN_HEADER_DEFAULT_TEXT = "Press the green button"


class IdleWidget(QWidget):
    class _State(Enum):
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

        # Setup live feed
        #
        self._live_feed: LiveFeedWidget = self.findChild(LiveFeedWidget, "liveFeed")
        self._live_feed.initialize(camera_info, config["viewfinderResolution"])
        self._live_feed.image_captured.connect(self._image_captured)
        self._live_feed.error.connect(self.error)

        # Countdown timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._countdown_timer_tick)

        # Setup RpiIo
        #
        self._io = RpiIoQtHelper(self, rpi_io)
        self._io.yes_button_pressed.connect(self._capture_requested)

        # Setup State
        #
        self._state = IdleWidget._State.Idle

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
        # This is a bit of a bodge, but the camera does usually become available pretty
        # quickly
        if self._state == IdleWidget._State.Idle:
            self._state = IdleWidget._State.Countdown
            self._countdown_timer_seconds_remaining = self._countdown_timer_seconds
            self._set_countdown_header_from_seconds_remaining()
            self._live_feed.prepare()
            self._timer.start(1000)
        else:
            logger.warning("Dropping capture request when in state: %s", self._state)

    def _countdown_timer_tick(self):
        if self._state == IdleWidget._State.Idle:
            logger.warning("Dropping countdown tick while in idle state")
        else:
            self._countdown_timer_seconds_remaining -= 1
            self._set_countdown_header_from_seconds_remaining()
            logger.debug(
                "Countdown timer tick: %s", self._countdown_timer_seconds_remaining
            )
            if self._countdown_timer_seconds_remaining <= 0:
                self._timer.stop()
                self._state = IdleWidget._State.AwaitingCapture
                self._live_feed.trigger_capture()

    def _image_captured(self, image: QImage):
        logger.debug("imageCaptured: %s", image)
        if self._state != IdleWidget._State.AwaitingCapture:
            logger.warning("Unexpected image captured while in state: %s", self._state)
        self._state = IdleWidget._State.Idle
        self._countdown_header.setText(COUNTDOWN_HEADER_DEFAULT_TEXT)
        self.image_captured.emit(image)

    def _set_countdown_header_from_seconds_remaining(self):
        self._countdown_header.setText(
            f"Get Ready: {self._countdown_timer_seconds_remaining}"
        )
