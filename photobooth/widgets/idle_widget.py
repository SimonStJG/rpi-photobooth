import logging
from enum import Enum

from PyQt5.QtCore import QRect, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QImage, QKeyEvent

from photobooth.camera import Camera
from photobooth.mask import Mask
from photobooth.rpi_io import RpiIo, RpiIoQtHelper
from photobooth.widgets.base_widget import BaseWidget
from photobooth.widgets.live_feed_widget import LiveFeedWidget

logger = logging.getLogger(__name__)


class IdleWidget(BaseWidget):
    class _State(Enum):
        Init = "Init"
        Idle = "Idle"
        Countdown = "Countdown"
        AwaitingCapture = "AwaitingCapture"

    image_captured = pyqtSignal(QImage)
    error = pyqtSignal(str)

    def __init__(
        self,
        config,
        mask: Mask,
        mask_offset,
        camera: Camera,
        rpi_io: RpiIo,
        parent=None,
    ):
        super().__init__(parent)
        gui_config = config["gui"]
        camera_config = config["camera"]

        self._mask = mask

        self._countdown_timer_seconds = gui_config.getint("countdownTimerSeconds")
        self._countdown_timer_seconds_remaining = None

        # Setup live feed
        #
        self._live_feed: LiveFeedWidget = LiveFeedWidget(
            camera, camera_config["isMirrored"], self._mask, parent=self,
        )
        self._live_feed.setGeometry(QRect(mask_offset, self._mask.size))
        self._live_feed.image_captured.connect(self._image_captured)
        self._live_feed.error.connect(self.error)
        self._live_feed.initialized.connect(self._on_live_feed_initialized)

        # Countdown timer
        self._timer = QTimer()
        self._timer.timeout.connect(self._countdown_timer_tick)

        # Setup RpiIo
        #
        self._io = RpiIoQtHelper(self, rpi_io)
        self._io.yes_button_pressed.connect(self._capture_requested)

        # Setup State
        #
        self._switch_to_init()

    def reload(self):
        self._live_feed.reload()

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)

        if event.key() in [Qt.Key_Space, Qt.Key_Enter]:
            event.accept()
            self._capture_requested()
        else:
            event.ignore()

    def _capture_requested(self):
        if self._state == IdleWidget._State.Idle:
            self._state = IdleWidget._State.Countdown
            self._countdown_timer_seconds_remaining = self._countdown_timer_seconds
            self._live_feed.set_overlay_text(
                str(self._countdown_timer_seconds_remaining)
            )
            self._live_feed.prepare()
            self._timer.start(1000)
        else:
            logger.warning("Dropping capture request when in state: %s", self._state)

    def _countdown_timer_tick(self):
        if self._state == IdleWidget._State.Idle:
            logger.warning("Dropping countdown tick while in idle state")
        else:
            self._countdown_timer_seconds_remaining -= 1
            self._live_feed.set_overlay_text(
                str(self._countdown_timer_seconds_remaining)
            )
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
        self._switch_to_init()
        self.image_captured.emit(image)

    def _switch_to_idle(self):
        self._live_feed.set_overlay_text("")
        self._state = IdleWidget._State.Idle

    def _switch_to_init(self):
        self._state = IdleWidget._State.Init
        self._live_feed.set_overlay_text("Wait..")

    def _on_live_feed_initialized(self):
        self._switch_to_idle()
        self._live_feed.set_overlay_text("")
