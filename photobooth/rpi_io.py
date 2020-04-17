import logging

from PyQt5.QtCore import QEvent, QObject, pyqtSignal

from gpio import Button

logger = logging.getLogger(__name__)


class RpiIo(QObject):
    yes_button_pressed = pyqtSignal()
    no_button_pressed = pyqtSignal()

    def __init__(self, rpi_io_config):
        self.yes_button = Button(rpi_io_config["yesButtonPin"])
        self.no_button = Button(rpi_io_config["noButtonPin"])

        self.yes_button.when_pressed = self.yes_button_pressed.emit
        self.no_button.when_pressed = self.no_button_pressed.emit


class RpiIoQtHelper(QObject):
    yes_button_pressed = pyqtSignal()
    no_button_pressed = pyqtSignal()

    def __init__(self, rpi_io: RpiIo, qobject: QObject):
        self._rpi_io = rpi_io
        self._qobject_name = qobject.__name__
        qobject.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            logger.debug("FocusIn: %s", self._qobject_name)
            self._rpi_io.yes_button_pressed.connect.self.yes_button_pressed
            self._rpi_io.no_button_pressed.connect.self.no_button_pressed
        elif event.type() == QEvent.FocusOut:
            logger.debug("FocusOut: %s", self._qobject_name)
            self._rpi_io.yes_button_pressed.disconnect.self.yes_button_pressed
            self._rpi_io.no_button_pressed.disconnect.self.no_button_pressed
