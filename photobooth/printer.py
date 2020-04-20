import logging
from datetime import datetime

import cups
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtGui import QImage

logger = logging.getLogger(__name__)


def printer_factory(printer_config):
    if printer_config.getboolean("useMockPrinter"):
        return MockPrinter()
    else:
        return LibCupsPrinter(printer_config)


class LibCupsPrinter(QObject):
    FILENAME = "/dev/shm/photobooth.jpg"
    STATE_CHECK_TIMER_MS = 500

    IPP_STATES = {
        cups.IPP_JOB_PENDING: "IPP_JOB_PENDING",
        cups.IPP_JOB_HELD: "IPP_JOB_HELD",
        cups.IPP_JOB_PROCESSING: "IPP_JOB_PROCESSING",
        cups.IPP_JOB_STOPPED: "IPP_JOB_STOPPED",
        cups.IPP_JOB_CANCELED: "IPP_JOB_CANCELED",
        cups.IPP_JOB_ABORTED: "IPP_JOB_ABORTED",
        cups.IPP_JOB_COMPLETED: "IPP_JOB_COMPLETED",
    }

    error = pyqtSignal(str)
    success = pyqtSignal()

    def __init__(self, printer_config):
        super().__init__()
        self._conn = cups.Connection()
        self._job_id = None

        requested_printer_name = printer_config["name"]
        requested_printer_name = (
            requested_printer_name if requested_printer_name != "" else None
        )

        self._printer = self._find_printer(requested_printer_name)

        # TODO Detect if printer online

        self._state_timer = QTimer()
        self._state_timer.timeout.connect(self._check_job_state)

        logger.info("Using printer: %s", self._printer)

    def print(self, image: QImage):
        job_title = datetime.now().strftime("photobooth-%y-%m-%d--%H-%M-%S")
        logger.debug("print: %s", job_title)
        image.save(LibCupsPrinter.FILENAME, "jpeg")
        try:
            # TODO Shrink file before printing to save a bit of ink
            self._job_id = self._conn.printFile(
                self._printer, LibCupsPrinter.FILENAME, job_title, {}
            )
        except cups.IPPError as e:
            logger.exception("Failed to call printFile")
            self.error.emit(f"Print failed: {str(e)}")
        self._state_timer.start(LibCupsPrinter.STATE_CHECK_TIMER_MS)

    def _check_job_state(self):
        def on_error(message):
            logger.error(message)
            self.error.emit(message)
            self._job_id = None
            self._state_timer.stop()

        def on_success():
            self.success.emit()
            self._job_id = None
            self._state_timer.stop()

        if self._job_id is None:
            on_error("Vanishing job ID")
        else:
            attribs = self._conn.getJobAttributes(self._job_id)
            logger.debug("attribs: %s", attribs)

            job_state = attribs["job-state"]
            job_printer_state_message = attribs["job-printer-state-message"]

            # TODO Notice if we are IPP_JOB_PENDING for too long
            if job_state in [cups.IPP_JOB_PROCESSING, cups.IPP_JOB_PENDING]:
                pass
            elif job_state == cups.IPP_JOB_COMPLETED:
                on_success()
            else:
                state_name = LibCupsPrinter.IPP_STATES.get(
                    job_state, f"unknown job state: {job_state}"
                )
                on_error(
                    f"Bad print state: {state_name}, "
                    f"message: {job_printer_state_message}"
                )

    def _find_printer(self, printer_name):
        all_printers = self._conn.getPrinters().keys()
        if printer_name is None:
            default_printer = self._conn.getDefault()
            if not default_printer:
                available_printers = ", ".join(all_printers)
                raise ValueError(
                    "No system default printer, please specify a printer in config, "
                    f"Available printers: {available_printers}"
                )
            return default_printer
        if printer_name not in all_printers:
            raise ValueError(
                "Unknown printer %s, known printers are: %s",
                printer_name,
                ", ".join(all_printers),
            )
        return printer_name


class MockPrinter(QObject):
    TIMEOUT_SECONDS = 5

    error = pyqtSignal(str)
    success = pyqtSignal()

    # noinspection PyUnusedLocal
    def __init__(self, *args, **kwargs):
        super().__init__()
        self._timer = None

    # noinspection PyUnusedLocal
    def print(self, image: QImage):
        self._timer = QTimer()
        self._timer.singleShot(
            MockPrinter.TIMEOUT_SECONDS * 1000, lambda: self.success.emit()
        )
