import logging

from PyQt5.QtCore import QEvent, Qt, pyqtSignal
from PyQt5.QtGui import QImage

from photobooth.mask import Mask
from photobooth.resources import images_root
from photobooth.rpi_io import RpiIo, RpiIoQtHelper
from photobooth.widgets.static_image_widget import StaticImageWidget

logger = logging.getLogger(__name__)


class ErrorWidget(StaticImageWidget):
    accept = pyqtSignal()

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
        self._io.no_button_pressed.connect(self.accept)

        image = QImage()
        if not image.load(str(images_root / "error.jpg")):
            raise ValueError("Failed to load error image")
        self.set_image(image)

    def set_error_message(self, text):
        self.set_text(f"Error: {text[:300]}")

    def keyPressEvent(self, event: QEvent):
        super().keyPressEvent(event)
        if event.key() in [Qt.Key_Space, Qt.Key_Escape]:
            event.accept()
            self.accept.emit()
        else:
            event.ignore()
