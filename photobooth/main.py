import logging
from configparser import ConfigParser

from PyQt5.QtMultimedia import QCameraInfo
from PyQt5.QtWidgets import QApplication
from more_itertools import one

from photobooth.main_window import MainWindow
from photobooth.printer import Printer
from photobooth.widgets.idle_widget import IdleWidget
from photobooth.widgets.preview_widget import PreviewWidget
from photobooth.widgets.printing_widget import PrintingWidget

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

    w = MainWindow(
        idle_widget=IdleWidget(camera_info),
        preview_widget=PreviewWidget(),
        printing_widget=PrintingWidget(),
        printer=Printer(),
    )
    w.showFullScreen()

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
            camera = one(matching_cameras, too_short=IndexError,)
        except ValueError as e:
            raise ValueError(
                f"Multiple cameras found with given device name ({requested_device_name})"
            ) from e
        except IndexError as e:
            available_cameras = ", ".join(
                c.deviceName() for c in QCameraInfo.availableCameras()
            )
            raise ValueError(
                f"No camera found with given device name ({requested_device_name}), "
                f"available devices: {available_cameras}"
            ) from e

    logging.info("Found QCamera: %s", camera.deviceName())
    return camera
