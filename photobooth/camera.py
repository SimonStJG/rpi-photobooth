import logging

from PyQt5.QtMultimedia import QCameraInfo

from photobooth.utils import one

logger = logging.getLogger(__name__)


def find_qcamera_info(requested_device_name):
    if requested_device_name is None or requested_device_name == "":
        camera = QCameraInfo.defaultCamera()
    else:
        matching_cameras = [
            c
            for c in QCameraInfo.availableCameras()
            if c.deviceName() == requested_device_name
        ]
        try:
            camera = one(matching_cameras)
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
