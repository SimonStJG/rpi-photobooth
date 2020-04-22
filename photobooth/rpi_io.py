import logging
import os
from contextlib import contextmanager
from pathlib import Path

from PyQt5.QtCore import QEvent, QObject, QTimer, pyqtSignal

logger = logging.getLogger(__name__)


class RpiIo(QObject):
    yes_button_pressed = pyqtSignal()
    no_button_pressed = pyqtSignal()


@contextmanager
def rpi_io_factory(rpi_io_config) -> RpiIo:
    if rpi_io_config.getboolean("useMockGpiozero"):
        logger.debug("Using mock gpiozero")
        button_factory = _MockGpioZeroButton
    else:
        logger.debug("Using real gpiozero")
        bounce_time_seconds = rpi_io_config.getfloat("bounceTimeSeconds")
        from gpiozero import Button

        @contextmanager
        def button_factory(*args, **kwargs):
            yield Button(*args, **kwargs, bounce_time=bounce_time_seconds)

    rpi_io = RpiIo()
    with button_factory(rpi_io_config["yesButtonPin"]) as yes_button:
        with button_factory(rpi_io_config["noButtonPin"]) as no_button:

            def when_yes_pressed():
                logger.warning("Yes pressed")
                rpi_io.yes_button_pressed.emit()

            yes_button.when_pressed = when_yes_pressed
            no_button.when_pressed = lambda: rpi_io.no_button_pressed.emit()
            yield rpi_io


class RpiIoQtHelper(QObject):
    yes_button_pressed = pyqtSignal()
    no_button_pressed = pyqtSignal()

    def __init__(self, qobject: QObject, rpi_io: RpiIo):
        super().__init__()
        self._rpi_io = rpi_io
        self._qobject_name = str(qobject)
        qobject.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            logger.debug("FocusIn: %s", self._qobject_name)
            self._rpi_io.yes_button_pressed.connect(self.yes_button_pressed)
            self._rpi_io.no_button_pressed.connect(self.no_button_pressed)
            return True

        if event.type() == QEvent.FocusOut:
            logger.debug("FocusOut: %s", self._qobject_name)
            self._rpi_io.yes_button_pressed.disconnect(self.yes_button_pressed)
            self._rpi_io.no_button_pressed.disconnect(self.no_button_pressed)
            return True

        return False


class _MockGpioZeroButton:
    """
    Mock button which can be triggered by writing to a named pipe
    """

    def __init__(self, pin):
        self._pipename = Path(f"{Path(__file__).parent.parent}/mock_button{pin}")
        self._timer = QTimer()
        self._timer.setInterval(200)
        self._timer.timeout.connect(self._check_for_button_press)
        self._timer.start()

    def __enter__(self):
        logger.debug("Creating pipe: %s", self._pipename)

        if os.path.exists(self._pipename):
            logger.warning("Pipe already exists, attempting to tidy it up")
            os.unlink(self._pipename)

        os.mkfifo(self._pipename)
        try:
            self._fd = os.open(self._pipename, os.O_RDWR | os.O_NONBLOCK)
            logger.debug("Opened pipe")
        except Exception:
            logger.exception("Failed to open fd")
            try:
                self._pipename.unlink()
            except Exception:
                logger.exception("Failed to unlink pipe: %s", self._pipename)
            raise

        self._timer.start()
        logger.debug("started timer")

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self._timer.stop()
        except Exception:
            logger.exception("Failed to stop timer")

        try:
            os.close(self._fd)
        except Exception:
            logger.exception("Failed to close fd: %s", self._fd)

        try:
            self._pipename.unlink()
        except Exception:
            logger.exception("Failed to unlink pipe: %s", self._pipename)

    def _check_for_button_press(self):
        try:
            os.read(self._fd, 10)
            logger.debug("Button press!")
            self.when_pressed()
        except BlockingIOError:
            pass

    def when_pressed(self):
        """
        Emulating how gpiozero works - this will be overriden later
        """
        pass
