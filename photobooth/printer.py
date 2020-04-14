import logging

import cups
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtGui import QImage

logger = logging.getLogger(__name__)

FILENAME = "/dev/shm/photobooth.jpg"
STATE_CHECK_TIMER_MS = 500


class Printer(QObject):
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
        self._state_timer = QTimer()
        self._state_timer.timeout.connect(self._check_job_state)

        logger.info("Using printer: %s", self._printer)

    def print(self, image: QImage):
        logger.debug("print: %s", image)
        image.save(FILENAME, "jpeg")
        self._job_id = self._conn.printFile(self._printer, FILENAME, "photobooth", {})
        self._state_timer.start(STATE_CHECK_TIMER_MS)

    def _check_job_state(self):
        def on_error(message):
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
            attribs = cups.getJobAttributes(self._job_id)
            logger.debug("Job state: %s", attribs)

            job_state = attribs["job-state"]

            # Legal states are:
            # INT_CONSTANT(IPP_JOB_PENDING);
            # INT_CONSTANT(IPP_JOB_HELD);
            # INT_CONSTANT(IPP_JOB_PROCESSING);
            # INT_CONSTANT(IPP_JOB_STOPPED);
            # INT_CONSTANT(IPP_JOB_CANCELED);
            # INT_CONSTANT(IPP_JOB_ABORTED);
            # INT_CONSTANT(IPP_JOB_COMPLETED);

            # TODO Notice if we are IPP_JOB_PENDING for too long
            if job_state in [cups.IPP_JOB_PROCESSING, cups.IPP_JOB_PENDING]:
                pass
            elif job_state == cups.IPP_JOB_COMPLETED:
                on_success()
            else:
                on_error("Bad print state: %s", job_state)

    def _find_printer(self, printer_name):
        if printer_name is None:
            printer = self._conn.getDefault()
            if not self._printer:
                raise ValueError(
                    "No system default printer, you need to specify a printer explicitly"
                )
        else:
            all_printers = self._conn.getPrinters()
            try:
                printer = all_printers[printer_name]
            except KeyError as e:
                raise ValueError(
                    "Unknown printer %s, known printers are: %s",
                    printer_name,
                    ", ".join(all_printers.keys()),
                ) from e
        return printer
