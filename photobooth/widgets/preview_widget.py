import logging

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent

from photobooth.mask import Mask
from photobooth.rpi_io import RpiIo, RpiIoQtHelper
from photobooth.widgets.static_image_widget import StaticImageWidget

logger = logging.getLogger(__name__)


class PreviewWidget(StaticImageWidget):
    accept = pyqtSignal()
    reject = pyqtSignal()

    def __init__(
        self,
        mask: Mask,
        mask_offset,
        rpi_io: RpiIo,
        parent=None,
        flags=Qt.WindowFlags(),
    ):
        super().__init__(mask, mask_offset, parent, flags)
        self._io = RpiIoQtHelper(self, rpi_io)
        self._io.yes_button_pressed.connect(self.accept)
        self._io.no_button_pressed.connect(self.reject)

        self.set_text("Press green to print")

    def keyPressEvent(self, event: QKeyEvent):
        super().keyPressEvent(event)

        if event.key() == Qt.Key_Space:
            event.accept()
            self.accept.emit()
        elif event.key() == Qt.Key_Escape:
            event.accept()
            self.reject.emit()
        else:
            event.ignore()
