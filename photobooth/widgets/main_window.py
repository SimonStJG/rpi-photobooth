import logging

from PyQt5.QtCore import QEvent, Qt, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QStackedWidget

from photobooth.widgets.error_widget import ErrorWidget
from photobooth.widgets.idle_widget import IdleWidget
from photobooth.widgets.preview_widget import PreviewWidget
from photobooth.widgets.printing_widget import PrintingWidget

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    quit = pyqtSignal()

    def __init__(
        self,
        parent=None,
        flags=Qt.WindowFlags(),
    ):
        super().__init__(parent, flags)

        self.setWindowTitle("Photobooth")

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

    def set_widgets(
        self,
        idle_widget: IdleWidget,
        preview_widget: PreviewWidget,
        printing_widget: PrintingWidget,
        error_widget: ErrorWidget,
    ):

        self.central_widget.addWidget(idle_widget)
        self.central_widget.addWidget(preview_widget)
        self.central_widget.addWidget(printing_widget)
        self.central_widget.addWidget(error_widget)

    def select_idle(self):
        self._select_by_index(0)

    def select_preview(self):
        self._select_by_index(1)

    def select_printing(self):
        self._select_by_index(2)

    def select_error(self):
        self._select_by_index(3)

    def keyPressEvent(self, event: QEvent):
        key = event.key()
        logger.info("keyPressEvent: %s", key)

        if key in [Qt.Key_Q]:
            event.accept()
            self.quit.emit()
        else:
            event.ignore()

    def _select_by_index(self, index):
        self.central_widget.setCurrentIndex(index)
