from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtGui import QColor, QImage, QPainter

_white = QColor("white")


class ScalingImageFormatter:
    """
    Scale the image content by scale_content, e.g. if the image is 200x200 and
    scale_factor is .5, then resulting image will still be 200x200, but the content
    will only occupy the central 100x100 pixels.
    """

    def __init__(self, mask, config):
        self._mask = mask

        scale_factor = float(config["scaleFactor"])
        if scale_factor > 1 or scale_factor < 0:
            raise ValueError("Only scale factors between 0 and 1 are valid")
        self._scale_factor = scale_factor

    def format_image(self, raw_image: QImage):
        masked = self._mask.mask(raw_image)

        image_size = masked.size()
        content_size = image_size * self._scale_factor
        image = QImage(image_size, raw_image.format())
        image.fill(_white)

        painter = QPainter(image)

        def get_image_content_rect():
            x = (image_size.width() - content_size.width()) / 2
            y = (image_size.height() - content_size.height()) / 2
            return QRect(QPoint(x, y), content_size)

        painter.drawImage(get_image_content_rect(), masked.scaled(content_size))
        painter.end()
        return image
