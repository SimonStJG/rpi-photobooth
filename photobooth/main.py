import argparse
import logging
from configparser import ConfigParser
from pathlib import Path

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication

from photobooth.camera import find_qcamera_info
from photobooth.image_formatter import ScalingImageFormatter
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
    args = _parse_args()

    logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)
    logging.getLogger("PyQt5.uic").setLevel(logging.INFO)

    config = _read_config(args.config)

    camera_info = find_qcamera_info(config["camera"]["deviceName"])

    app = QApplication([])
    app.setApplicationName(APPLICATION_NAME)

    _load_fonts()

    with rpi_io_factory(config["rpiIo"]) as rpi_io:
        main_window = MainWindow()

        idle_widget = IdleWidget(config["gui"], camera_info, rpi_io, parent=main_window)
        preview_widget = PreviewWidget(rpi_io, parent=main_window)
        printing_widget = PrintingWidget(parent=main_window)
        error_widget = ErrorWidget(rpi_io, parent=main_window)
        image_formatter = ScalingImageFormatter(config["printer"])
        printer = printer_factory(config["printer"], image_formatter)

        main_window.set_widgets(
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
            config=config["gui"],
        )

        with (stylesheets_root / "main.qss").open("r") as stylesheet:
            app.setStyleSheet(stylesheet.read())

        main_window.showFullScreen()

        app.exec_()


def _parse_args():
    parser = argparse.ArgumentParser(description="Photobooth")
    parser.add_argument("--config", help="Config file to use", default=None)
    return parser.parse_args()


def _read_config(requested_config_location):
    if requested_config_location is None:
        logger.warning("No config passed, using default config")
        config_location = str(Path(__file__).parent.parent / "default-config.cfg")
    else:
        logger.debug("Resolving config: %s", requested_config_location)
        config_location = str(Path(requested_config_location).resolve())

    config = ConfigParser()
    if config_location not in config.read(config_location):
        raise ValueError("Failed to read config: %s", config_location)

    return config


def _load_fonts():
    font_database = QtGui.QFontDatabase()
    for font_location in fonts_root.glob("**/*.ttf"):
        logger.debug("Found font: %s", font_location)
        font_database.addApplicationFont(str(font_location))
