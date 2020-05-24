from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QImage, QPixmap, QResizeEvent
from PyQt5.QtWidgets import QLabel

from photobooth.mask import Mask
from photobooth.widgets.base_widget import BaseWidget


class StaticImageWidget(BaseWidget):
    def __init__(self, mask: Mask, mask_offset, parent=None, flags=Qt.WindowFlags()):
        super().__init__(parent, flags)

        self._mask = mask
        self._image = None

        self._imageLabel: QLabel = QLabel(parent=self)
        self._imageLabel.setMask(self._mask.clip_region)
        self._imageLabel.setGeometry(QRect(mask_offset, self._mask.size))

        self._text = QLabel(parent=self)
        self._text.setAlignment(Qt.AlignCenter)

    def resizeEvent(self, event: QResizeEvent) -> None:
        text_bounding_rect_height = self.height() / 2
        self._text.setGeometry(
            QRect(
                0,
                self.height() - text_bounding_rect_height,
                self.width(),
                text_bounding_rect_height,
            )
        )

        if self._image:
            self._load_image_into_imagelabel()

    def set_image(self, image: QImage):
        self._image = image
        self._load_image_into_imagelabel()

    def set_text(self, text: str):
        self._text.setText(text)

    def _load_image_into_imagelabel(self):
        self._imageLabel.setPixmap(
            QPixmap.fromImage(
                self._mask.shrink_and_clip_to_mask_size(self._image), Qt.AutoColor
            )
        )
