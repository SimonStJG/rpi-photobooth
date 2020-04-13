import logging

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QImage

logger = logging.getLogger(__name__)

import cups

class Printer(QObject):
    state_change = pyqtSignal(int)

    def __init__(self):
        super().__init__()
        # self._printer = QPrinter(QPrinter.HighResolution)
        #
        # self._printer.setOrientation(QPrinter.Landscape)
        # # TODO Inject this info from config
        # self._printer.setPageMargins(20, 20, 20, 20, QPrinter.Millimeter)
        # self._printer.setFullPage(False)
        # self._printer.setPageSize(QPrinter.A6)
        # self._printer.setColorMode(QPrinter.Color)
        self._conn = cups.Connection()
        self._printer = self._conn.getDefault()
        logger.info("Using printer: %s", self._printer)

    def print(self, image: QImage):
        logger.debug("print: %s", image)
        image.save("/dev/shm/p1.jpg", "jpeg")
        self._conn.printFile(self._printer, "/dev/shm/p1.jpg", "photobooth", {})