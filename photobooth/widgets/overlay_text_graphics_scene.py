import logging

from PyQt5.QtCore import QRectF, QSize, Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QGraphicsScene

logger = logging.getLogger(__name__)


class OverlayTextGraphicsScene(QGraphicsScene):
    """
    A QGraphicsScene which will draw some text in the center of the foreground
    """

    def __init__(self, size: QSize):
        super().__init__()
        self._overlay_text = None

        # Get the default font and guess at the best size for it
        self._font = QPainter().font()
        self._font.setPixelSize(min(size.height(), size.width()) / 2)

    def set_overlay_text(self, overlay_text):
        self._overlay_text = overlay_text

    def drawForeground(self, painter: QPainter, rect: QRectF) -> None:
        super().drawForeground(painter, rect)
        if self._overlay_text:
            painter.setFont(self._font)
            painter.drawText(rect, Qt.AlignCenter, self._overlay_text)
