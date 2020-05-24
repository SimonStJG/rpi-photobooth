from PyQt5.QtCore import Qt

from photobooth.mask import Mask
from photobooth.widgets.static_image_widget import StaticImageWidget


class PrintingWidget(StaticImageWidget):
    def __init__(self, mask: Mask, mask_offset, parent=None, flags=Qt.WindowFlags()):
        super().__init__(mask, mask_offset, parent=parent, flags=flags)
        self.set_text("Printing")
