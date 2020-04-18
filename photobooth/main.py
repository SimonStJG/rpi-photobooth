import logging
from configparser import ConfigParser

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication

from photobooth.camera import find_qcamera_info
from photobooth.main_controller import MainController
from photobooth.printer import printer_factory
from photobooth.resources import fonts_root, stylesheets_root
from photobooth.rpi_io import rpi_io_factory
from photobooth.widgets.error_widget import ErrorWidget
from photobooth.widgets.idle_widget import IdleWidget
from photobooth.widgets.main_window import MainWindow
from photobooth.widgets.preview_widget import PreviewWidget
from photobooth.widgets.printing_widget import PrintingWidget

logger = logging.getLogger(__name__)

APPLICATION_NAME = "photobooth"
LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"


def main():
    logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)
    logging.getLogger("PyQt5.uic").setLevel(logging.INFO)

    config = ConfigParser()
    # TODO Inject config name
    config.read("./photobooth.cfg")

    camera_info = find_qcamera_info(config["camera"]["deviceName"])

    app = QApplication([])
    app.setApplicationName(APPLICATION_NAME)

    _load_fonts()

    with rpi_io_factory(config["rpiIo"]) as rpi_io:
        idle_widget = IdleWidget(camera_info, rpi_io)
        preview_widget = PreviewWidget(rpi_io)
        printing_widget = PrintingWidget()
        error_widget = ErrorWidget(rpi_io)
        printer = printer_factory(config["printer"])

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

        with (stylesheets_root / "main.qss").open("r") as stylesheet:
            app.setStyleSheet(stylesheet.read())

        main_window.showFullScreen()

        app.exec_()


def _load_fonts():
    font_database = QtGui.QFontDatabase()
    for font_location in fonts_root.glob("**/*.tff"):
        logger.debug("Found font: %s", font_location)
        font_database.addApplicationFont(font_location)
