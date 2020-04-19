import logging

from PyQt5.QtWidgets import QGridLayout, QMainWindow, QWidget

logger = logging.getLogger(__name__)


def set_grid_content_margins(widget: QWidget):
    # This is not possible via qss https://bugreports.qt.io/browse/QTBUG-22862 so this
    #   bodge will have to do.
    grid_layout = widget.findChild(QGridLayout, "gridLayout")
    parent = widget.parent()
    if not isinstance(parent, QMainWindow):
        raise ValueError(
            f"Expected parent to be instance of QMainWindow but was {parent}"
        )
    content_margin = min(parent.height(), parent.width()) / 8
    logger.debug("Setting content margin: %s", content_margin)

    grid_layout.setContentsMargins(*([content_margin] * 4))
