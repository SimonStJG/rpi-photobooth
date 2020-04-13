import logging

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QImage
from PyQt5.QtPrintSupport import QPrinter
from PyQt5.QtWidgets import QMainWindow, QStackedWidget

from photobooth.printer import Printer
from photobooth.state import Idle, Preview, Printing
from photobooth.widgets.idle_widget import IdleWidget
from photobooth.widgets.preview_widget import PreviewWidget
from photobooth.widgets.printing_widget import PrintingWidget

WINDOW_TITLE = "photobooth"

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(
        self,
        idle_widget: IdleWidget,
        preview_widget: PreviewWidget,
        printing_widget: PrintingWidget,
        printer: Printer,
        parent=None,
        flags=Qt.WindowFlags(),
    ):
        super().__init__(parent, flags)

        self.idle_widget = idle_widget
        self.preview_widget = preview_widget
        self.printing_widget = printing_widget
        self.printer = printer

        self.state = Idle()

        self.setWindowTitle(WINDOW_TITLE)

        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        self.central_widget.addWidget(idle_widget)
        self.central_widget.addWidget(preview_widget)
        self.central_widget.addWidget(printing_widget)

        # Wire it all up
        self.idle_widget.imageCaptured.connect(self._idle__image_captured)
        self.preview_widget.accept.connect(self._preview__print_image)
        self.preview_widget.reject.connect(self._preview__reject_image)
        self.printer.state_change.connect(self._printer__state_change)

    def keyPressEvent(self, event: QEvent):
        key = event.key()
        logger.debug("keyPressEvent: %s", key)

        if key in [Qt.Key_Q]:
            event.accept()
            self.deleteLater()
        else:
            event.ignore()

    def _reset(self):
        self.central_widget.setCurrentIndex(0)

    def _idle__image_captured(self, image: QImage):
        if isinstance(self.state, Idle):
            self.state = Preview(image)
            self.last_captured_image = image
            self.preview_widget.set_state(self.state)
            self.central_widget.setCurrentIndex(1)
        else:
            logger.warning(
                "Dropping unexpected _idle__image_captured while in %s state",
                self.state,
            )

    def _preview__print_image(self):
        if isinstance(self.state, Preview):
            self.state = Printing(self.state.image)
            self.printing_widget.set_state(self.state)
            self.central_widget.setCurrentIndex(2)
            self.printer.print(self.state.image)
        else:
            logger.warning(
                "Dropping unexpected _preview__print_image while in %s state",
                self.state,
            )

    def _preview__reject_image(self):
        if isinstance(self.state, Preview):
            self.state = Idle()
            self.central_widget.setCurrentIndex(0)
        else:
            logger.warning(
                "Dropping unexpected _preview__reject_image while in %s state",
                self.state,
            )

    def _printer__state_change(self, printer_state):
        if not isinstance(self.state, Printing):
            logger.error(
                "Unexpected printer state change while not in printing mode: %s %s",
                self.state, printer_state,
            )
            # TODO Die
        else:
            if self.state in [QPrinter.Aborted, QPrinter.Error]:
                logger.error("Bad printer state change")
                # TODO Die
            elif self.state == QPrinter.Active:
                logger.info("Printer state is Active")
            elif self.state == QPrinter.Idle:
                # Could be cleverer here and check it transitioned to active first
                logger.info("Printer state is Idle")
                self.state = Idle
                self.central_widget.setCurrentIndex(0)
            else:
                raise NotImplementedError()
