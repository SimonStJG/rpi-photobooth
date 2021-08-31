import argparse
import logging
import signal
from configparser import ConfigParser
from pathlib import Path

from PyQt5 import QtGui
from PyQt5.QtCore import QPoint, QSize
from PyQt5.QtWidgets import QApplication

from photobooth.camera import Camera
from photobooth.image_formatter import ScalingImageFormatter
from photobooth.main_controller import MainController
from photobooth.mask import Mask
from photobooth.printer import printer_factory
from photobooth.resources import fonts_root, images_root, stylesheets_root
from photobooth.rpi_io import rpi_io_factory
from photobooth.widgets.error_widget import ErrorWidget
from photobooth.widgets.idle_widget import IdleWidget
from photobooth.widgets.main_window import MainWindow
from photobooth.widgets.preview_widget import PreviewWidget
from photobooth.widgets.printing_widget import PrintingWidget

logger = logging.getLogger(__name__)

APPLICATION_NAME = "photobooth"
LOG_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"


def _sigint_handler(app):
    def handler():
        logger.fatal("Caught sigint")
        app.quit()

    return handler


_screen_config = {
    (1366, 768): {
        "screen_size": QSize(1366, 768),
        "stylesheet": "1366x768.qss",
        # Mask which will be applied to all images taken with the camera
        # before display on the screen or printing
        "mask": "1366x768-mask-cropped.png",
        # Where the top left hand corner of the mask sits on the background
        "mask_offset": QPoint(370, 158),
    },
    (1920, 1080): {
        "screen_size": QSize(1920, 1080),
        "stylesheet": "1920x1080.qss",
        # Mask which will be applied to all images taken with the camera
        # before display on the screen or printing
        "mask": "1920x1080-mask-cropped.png",
        # Where the top left hand corner of the mask sits on the background
        "mask_offset": QPoint(518, 220),
    },
    (800, 480): {
        "screen_size": QSize(800, 480),
        "stylesheet": "800x480.qss",
        # Mask which will be applied to all images taken with the camera
        # before display on the screen or printing
        "mask": "800x480-mask-cropped.png",
        # Where the top left hand corner of the mask sits on the background
        "mask_offset": QPoint(101, 82),
    },
}


def main():
    args = _parse_args()

    logging.basicConfig(format=LOG_FORMAT, level=logging.DEBUG)

    config = _read_config(args.config)

    app = QApplication([])
    app.setApplicationName(APPLICATION_NAME)

    screen_config = _get_screen_config(app)

    signal.signal(signal.SIGINT, _sigint_handler(app))

    _load_fonts()

    camera = Camera(config["camera"])
    mask = Mask(images_root / screen_config["mask"])

    with rpi_io_factory(config["rpiIo"]) as rpi_io:
        main_window = MainWindow()

        idle_widget = IdleWidget(
            config=config,
            mask=mask,
            mask_offset=screen_config["mask_offset"],
            camera=camera,
            rpi_io=rpi_io,
            parent=main_window,
        )
        preview_widget = PreviewWidget(
            mask=mask,
            mask_offset=screen_config["mask_offset"],
            rpi_io=rpi_io,
            parent=main_window,
        )
        printing_widget = PrintingWidget(
            mask=mask, mask_offset=screen_config["mask_offset"], parent=main_window
        )
        error_widget = ErrorWidget(
            mask=mask,
            mask_offset=screen_config["mask_offset"],
            rpi_io=rpi_io,
            parent=main_window,
        )
        image_formatter = ScalingImageFormatter(mask, config["printer"])
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

        with (stylesheets_root / screen_config["stylesheet"]).open("r") as stylesheet:
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


def _get_screen_config(app):
    screensize = app.desktop().screenGeometry().size()
    screensize_as_tuple = screensize.width(), screensize.height()
    try:
        screen_config = _screen_config[screensize_as_tuple]
    except KeyError:
        raise ValueError(
            f"Unsupported resolution: {screensize} - only supported sizes are "
            f"{', '.join(_screen_config.keys())}.  See main.py for how to add "
            f"more"
        )
    return screen_config


def _load_fonts():
    font_database = QtGui.QFontDatabase()
    for font_location in fonts_root.glob("**/*.ttf"):
        logger.debug("Found font: %s", font_location)
        font_database.addApplicationFont(str(font_location))
