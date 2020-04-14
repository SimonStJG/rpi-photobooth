import logging
from dataclasses import dataclass

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage

from photobooth.printer import Printer
from photobooth.ui.error_widget import ErrorWidget
from photobooth.ui.idle_widget import IdleWidget
from photobooth.ui.main_window import MainWindow
from photobooth.ui.preview_widget import PreviewWidget
from photobooth.ui.printing_widget import PrintingWidget

logger = logging.getLogger(__name__)


class MainController:
    class Idle:
        pass

    @dataclass
    class Preview:
        image: QImage

    @dataclass
    class Printing:
        image: QImage

    @dataclass
    class Error:
        message: str

    def __init__(
        self,
        main_window: MainWindow,
        idle_widget: IdleWidget,
        preview_widget: PreviewWidget,
        printing_widget: PrintingWidget,
        error_widget: ErrorWidget,
        printer: Printer,
    ):
        self.main_window = main_window
        self.idle_widget = idle_widget
        self.preview_widget = preview_widget
        self.printing_widget = printing_widget
        self.error_widget = error_widget
        self.printer = printer

        self.idle_widget.error.connect(self._on_error)
        self.idle_widget.image_captured.connect(self._idle__image_captured)

        self.preview_widget.accept.connect(self._preview__accept)
        self.preview_widget.reject.connect(self._preview__reject)

        self.error_widget.accept.connect(self._error__accept)

        self.main_window.quit.connect(self._main_window__quit)

    @pyqtSlot
    def _error__accept(self):
        self.main_window.select_idle()

    @pyqtSlot
    def _idle__image_captured(self, image: QImage):
        if isinstance(self.state, MainController.Idle):
            self.state = MainController.Preview(image)
            self.last_captured_image = image
            self.preview_widget.set_image(image)
            self.main_window.select_preview()
        else:
            logger.warning(
                "Dropping unexpected _idle__image_captured while in %s state",
                self.state,
            )

    @pyqtSlot
    def _preview__accept(self):
        if isinstance(self.state, MainController.Preview):
            self.state = MainController.Printing(self.state.image)
            self.printing_widget.set_image(self.state.image)
            self.main_window.select_printing()
            self.printer.print(self.state.image)
        else:
            logger.warning(
                "Dropping unexpected _preview__print_image while in %s state",
                self.state,
            )

    @pyqtSlot
    def _preview__reject(self):
        if isinstance(self.state, MainController.Preview):
            self.state = MainController.Idle()
            self.main_window.select_idle()
        else:
            logger.warning(
                "Dropping unexpected _preview__reject_image while in %s state",
                self.state,
            )

    @pyqtSlot
    def _printer__success(self):
        if isinstance(self.state, MainController.Printing):
            self.state = MainController.Idle()
            self.main_window.select_idle()
        else:
            logger.warning(
                "Dropping unexpected _printer__success while in %s state", self.state
            )

    @pyqtSlot
    def _on_error(self, message):
        logger.error("_on_error: %s", message)
        self.state = MainController.Error(message)
        self.main_window.select_error()
        self.error_widget.set_message(message)

    @pyqtSlot
    def _main_window__quit(self):
        logger.info("_main_window__quit")
        self.main_window.deleteLater()
