from configparser import ConfigParser

from PyQt5.QtWidgets import QApplication, QLabel
from PyQt5.QtMultimedia import QCameraInfo

def main():
    # TODO Inject 
    config = ConfigParser()
    config.read('./photobooth.cfg')

    app = QApplication([])

    deviceName = config['camera']['deviceName']
    try:
    camera = one(c for c in QCameraInfo.availableCameras() if c.deviceName() == )
    import pdb
    pdb.set_trace()

    label = QLabel('Hello World!')
    label.show()
    app.exec_()
