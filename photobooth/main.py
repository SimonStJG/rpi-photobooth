from configparser import ConfigParser

from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QCameraInfo, QCamera
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtWidgets import QApplication, QMainWindow
from more_itertools import one


APPLICATION_NAME = 'photobooth'


class PreviewWindow(QMainWindow):
    def __init__(self, camera_info, parent=None, flags=Qt.WindowFlags()):
        super(PreviewWindow, self).__init__(parent, flags)

        self.setWindowTitle(APPLICATION_NAME)

        self.view_finder = QCameraViewfinder()
        self.setCentralWidget(self.view_finder)

        self.camera = QCamera(camera_info)
        self.camera.setViewfinder(self.view_finder)
        self.camera.start()

    def keyPressEvent(self, event):
        super(PreviewWindow, self).keyPressEvent(event)
        if event.key() in [Qt.Key_Q, Qt.Key_Escape]:
            self.deleteLater()


def main():
    # TODO Inject config name
    config = ConfigParser()
    config.read('./photobooth.cfg')

    app = QApplication([])
    app.setApplicationName(APPLICATION_NAME)

    qcamera_info = find_qcamera_info(config['camera']['deviceName'])

    print(qcamera_info)

    w = PreviewWindow(qcamera_info)
    w.showFullScreen()

    app.exec_()


def find_qcamera_info(requested_device_name):
    if requested_device_name is None or requested_device_name == "":
        camera = QCameraInfo.defaultCamera()
    else:
        try:
            camera = one(
                [c for c in QCameraInfo.availableCameras() if c.deviceName() == requested_device_name],
                too_short=IndexError
            )
        except ValueError as e:
            raise ValueError(f"Multiple cameras found with given device name ({requested_device_name})") from e
        except IndexError as e:
            available_cameras = ", ".join(c.deviceName() for c in QCameraInfo.availableCameras())
            raise ValueError(f"No camera found with given device name ({requested_device_name}), "
                             f"available devices: {available_cameras}") from e
    return camera
