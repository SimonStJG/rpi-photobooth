import logging
from configparser import ConfigParser

from more_itertools import one
from PyQt5.QtMultimedia import QCameraInfo
from PyQt5.QtWidgets import QApplication

from photobooth.main_controller import MainController
from photobooth.printer import Printer
from photobooth.rpi_io import rpi_io_factory
from photobooth.ui.error_widget import ErrorWidget
from photobooth.ui.idle_widget import IdleWidget
from photobooth.ui.main_window import MainWindow
from photobooth.ui.preview_widget import PreviewWidget
from photobooth.ui.printing_widget import PrintingWidget

logger = logging.getLogger(__name__)

APPLICATION_NAME = "photobooth"
LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"


def main():
    logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)

    config = ConfigParser()
    # TODO Inject config name
    config.read("./photobooth.cfg")

    camera_info = _find_qcamera_info(config["camera"]["deviceName"])

    app = QApplication([])
    app.setApplicationName(APPLICATION_NAME)

    with rpi_io_factory(config["rpiIo"]) as rpi_io:
        idle_widget = IdleWidget(camera_info, rpi_io)
        preview_widget = PreviewWidget(rpi_io)
        printing_widget = PrintingWidget()
        error_widget = ErrorWidget(rpi_io)
        printer = Printer(config["printer"])

        main_window = MainWindow(
            idle_widget=idle_widget,
            preview_widget=preview_widget,
            printing_widget=printing_widget,
            error_widget=error_widget,
        )
        main_controller = MainController(  # NoQA: Unused variable
            main_window=main_window,
            idle_widget=idle_widget,
            preview_widget=preview_widget,
            printing_widget=printing_widget,
            error_widget=error_widget,
            printer=printer,
        )

        main_window.showFullScreen()

        app.exec_()


def _find_qcamera_info(requested_device_name):
    if requested_device_name is None or requested_device_name == "":
        camera = QCameraInfo.defaultCamera()
    else:
        matching_cameras = [
            c
            for c in QCameraInfo.availableCameras()
            if c.deviceName() == requested_device_name
        ]
        try:
            camera = one(matching_cameras, too_short=IndexError)
        except ValueError as e:
            raise ValueError(
                "Multiple cameras found with requested device name: "
                f"{requested_device_name}"
            ) from e
        except IndexError as e:
            available_cameras = ", ".join(
                c.deviceName() for c in QCameraInfo.availableCameras()
            )
            raise ValueError(
                "No camera found with requested device name: "
                f"{requested_device_name}, available devices: "
                f"{available_cameras}"
            ) from e

    logging.info("Found QCamera: %s", camera.deviceName())
    return camera
