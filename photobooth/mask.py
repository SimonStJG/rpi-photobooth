import logging
from pathlib import Path

from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QColor, QImage, QPainter, QPixmap, QRegion

logger = logging.getLogger(__name__)


class Mask:
    def __init__(self, mask_path: Path):
        mask_pix = QPixmap()
        if not mask_pix.load(str(mask_path)):
            raise ValueError(f"Failed to load mask from {mask_path}")

        self.size = mask_pix.size()
        logger.debug("size: %s", self.size)

        self.clip_region = QRegion(
            mask_pix.createMaskFromColor(QColor("white"), Qt.MaskInColor)
        )
        logger.debug("clip_region: %s", self.clip_region)
        logger.debug("clip_region bounding rect: %s", self.clip_region.boundingRect())

    def mask(self, image: QImage) -> QImage:
        clip_rect = self._build_clip_rect(image)

        masked = QImage(self.size, QImage.Format_RGB32)

        painter = QPainter(masked)
        painter.setRenderHints(QPainter.Antialiasing, QPainter.SmoothPixmapTransform)
        painter.setClipRegion(self.clip_region)
        painter.drawImage(masked.rect(), image, clip_rect)

        painter.end()

        return masked

    def shrink_and_clip_to_mask_size(self, image):
        clip_rect = self._build_clip_rect(image)

        shrunk_and_clipped = QImage(self.size, QImage.Format_RGB32)

        painter = QPainter(shrunk_and_clipped)
        painter.setRenderHints(QPainter.Antialiasing, QPainter.SmoothPixmapTransform)
        painter.drawImage(shrunk_and_clipped.rect(), image, clip_rect)

        painter.end()

        return shrunk_and_clipped

    def _build_clip_rect(self, image):
        logger.debug("Image size: %s", image.size())
        image_height_for_width = image.height() / image.width()
        mask_height_for_width = float(self.size.height()) / self.size.width()
        logger.debug(
            "Height for widths - image: %s mask: %s",
            image_height_for_width,
            mask_height_for_width,
        )
        if image_height_for_width > mask_height_for_width:
            # image is taller than mask
            clip_height = int(image.size().width() * mask_height_for_width)
            clip_rect = QRect(
                0,
                (image.size().height() - clip_height) / 2,
                image.size().width(),
                clip_height,
            )
        else:
            # image is wider than mask
            clip_width = int(image.size().height() / mask_height_for_width)
            clip_rect = QRect(
                (image.size().width() - clip_width) / 2,
                0,
                clip_width,
                image.size().height(),
            )
        logger.debug("Clip rect: %s", clip_rect)
        return clip_rect
