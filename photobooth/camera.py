import logging

from PyQt5.QtMultimedia import QCamera, QCameraInfo, QCameraViewfinderSettings

from photobooth.utils import is_none_or_empty, one, to_qsize

logger = logging.getLogger(__name__)


class Camera(QCamera):
    def __init__(self, config) -> None:
        super().__init__(_find_camera_info(config["deviceName"]))

        if is_none_or_empty(config["viewfinderResolution"]):
            self._requested_viewfinder_resolution = None
        else:
            self._requested_viewfinder_resolution = to_qsize(
                config["viewfinderResolution"]
            )

        self.statusChanged.connect(self._on_status_changed)

    def _on_status_changed(self, status: QCamera.Status) -> None:
        logger.debug("_on_camera_status_changed: %s", status)
        if status == QCamera.LoadedStatus:
            supported_resolutions = self.supportedViewfinderResolutions()
            logger.info("Supported view finder resolutions: %s", supported_resolutions)
            if self._requested_viewfinder_resolution:
                if self._requested_viewfinder_resolution in supported_resolutions:
                    logger.info(
                        "Setting resolution to %s",
                        self._requested_viewfinder_resolution,
                    )
                    requested_settings = QCameraViewfinderSettings()
                    requested_settings.setResolution(
                        self._requested_viewfinder_resolution
                    )
                    self.setViewfinderSettings(requested_settings)
                else:
                    raise ValueError(
                        "Requested viewfinder resolution %s, "
                        "but the only supported resolutions are %s",
                        ", ".join(map(str, supported_resolutions)),
                    )

            camera_resolution = self.viewfinderSettings().resolution()
            logger.info("Using resolution: %s", camera_resolution)


def _find_camera_info(requested_device_name):
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
