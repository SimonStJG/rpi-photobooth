from PyQt5 import uic

from photobooth.resources import ui_root


def load_ui(ui_file, baseinstance):
    uic.loadUi(str(ui_root / ui_file), baseinstance, "photobooth.widgets")
