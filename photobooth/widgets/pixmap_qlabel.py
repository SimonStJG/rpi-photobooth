from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QLabel


class PixmapQLabel(QLabel):
    """Borrowed from https://stackoverflow.com/a/22618496"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._raw_pixmap = None

    def heightForWidth(self, width: int) -> int:
        if self._raw_pixmap:
            return float(self._raw_pixmap.height() * width) / self._raw_pixmap.width()
        else:
            return self.height()

    def sizeHint(self) -> QtCore.QSize:
        width = self.width()
        return QSize(width, self.heightForWidth(width))

    def setPixmap(self, pixmap: QtGui.QPixmap) -> None:
        self._raw_pixmap = pixmap
        super().setPixmap(self._scaled_pixmap())

    def resizeEvent(self, e: QtGui.QResizeEvent) -> None:
        if self._raw_pixmap:
            self.setPixmap(self._scaled_pixmap())

    def _scaled_pixmap(self):
        return self._raw_pixmap.scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
