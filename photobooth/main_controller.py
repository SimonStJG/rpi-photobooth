import inspect
import logging
from dataclasses import dataclass

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage

from photobooth.printer import LibCupsPrinter
from photobooth.widgets.error_widget import ErrorWidget
from photobooth.widgets.idle_widget import IdleWidget
from photobooth.widgets.main_window import MainWindow
from photobooth.widgets.preview_widget import PreviewWidget
from photobooth.widgets.printing_widget import PrintingWidget

logger = logging.getLogger(__name__)


class MainController:

    # States
    #

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
        printer: LibCupsPrinter,
        config,
    ):
        super().__init__()
        self._main_window = main_window
        self._idle_widget = idle_widget
        self._preview_widget = preview_widget
        self._printing_widget = printing_widget
        self._error_widget = error_widget
        self._printer = printer
        self._error_timeout_seconds = config.getint("errorTimeoutSeconds")
        self._preview_timeout_seconds = config.getint("previewTimeoutSeconds")

        self._timeout_timer = QTimer()

        # Connect signals
        #

        self._idle_widget.error.connect(self._switch_to_error)
        self._idle_widget.image_captured.connect(
            self._expect_state_then_switch(MainController.Idle, self._switch_to_preview)
        )

        self._preview_widget.accept.connect(
            self._expect_state_then_switch(
                MainController.Preview, self._switch_to_printing
            )
        )
        self._preview_widget.reject.connect(
            self._expect_state_then_switch(MainController.Preview, self._switch_to_idle)
        )

        self._printer.error.connect(self._switch_to_error)
        self._printer.success.connect(
            self._expect_state_then_switch(
                MainController.Printing, self._switch_to_idle,
            )
        )

        self._error_widget.accept.connect(
            self._expect_state_then_switch(MainController.Error, self._switch_to_idle)
        )

        self._main_window.quit.connect(self._main_window.deleteLater)

        # Initialise state
        #

        self._switch_to_idle()

    def _cancel_timeouts(self):
        self._timeout_timer.stop()

    def _expect_state_then_switch(self, expected_state, switch_to):
        def _inner(*args, **kwargs):
            caller = inspect.stack()[1][3]
            if isinstance(self.state, expected_state):
                logger.debug("Caught %s while in %s state", caller, self.state)
                switch_to(*args, **kwargs)
            else:
                logger.warning(
                    "Dropping unexpected %s while in %s state", caller, self.state
                )

        return _inner

    def _switch_to_idle(self):
        self._cancel_timeouts()
        self.state = MainController.Idle()
        self._idle_widget.reload()
        self._main_window.select_idle()

    def _switch_to_preview(self, image):
        self._cancel_timeouts()
        self.state = MainController.Preview(image)
        self.last_captured_image = image
        self._preview_widget.set_image(image)
        self._main_window.select_preview()
        self._timeout_timer.singleShot(
            self._preview_timeout_seconds * 1000,
            self._expect_state_then_switch(
                MainController.Preview, self._switch_to_idle
            ),
        )

    def _switch_to_printing(self):
        self._cancel_timeouts()
        self.state = MainController.Printing(self.state.image)
        self._printing_widget.set_image(self.state.image)
        self._main_window.select_printing()
        self._printer.print(self.state.image)

    def _switch_to_error(self, message: str):
        logger.error("_on_error: %s", message)
        self._cancel_timeouts()
        self.state = MainController.Error(message)
        self._main_window.select_error()
        self._error_widget.set_error_message(message)
        self._timeout_timer.singleShot(
            self._error_timeout_seconds * 1000,
            self._expect_state_then_switch(MainController.Error, self._switch_to_idle),
        )
