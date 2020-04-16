import logging

import cups
from PyQt5.QtCore import QObject, QTimer, pyqtSignal
from PyQt5.QtGui import QImage

logger = logging.getLogger(__name__)

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
            print(job_state)

            # TODO Notice if we are IPP_JOB_PENDING for too long
            if job_state in [cups.IPP_JOB_PROCESSING, cups.IPP_JOB_PENDING]:
                pass
            elif job_state == cups.IPP_JOB_COMPLETED:
                on_success()
            else:
                state_name = IPP_STATES.get(job_state, "unknown job state: {job_state}")
                on_error(
                    f"Bad print state: {state_name}, "
                    f"message: {job_printer_state_message}"
                )

    def _find_printer(self, printer_name):
        if printer_name is None:
            printer = self._conn.getDefault()
            if not printer:
                available_printers = ", ".join(self._conn.getPrinters().values())
                raise ValueError(
                    "No system default printer, please specify a printer in config, "
                    f"Available printers: {available_printers}"
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
