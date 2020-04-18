from PyQt5.QtWidgets import QGridLayout

GRID_LAYOUT_CONTENT_MARGIN = 100


def set_grid_content_margins(grid_layout: QGridLayout):
    # This is not possible via qss https://bugreports.qt.io/browse/QTBUG-22862 so this
    #   bodge will have to do.
    grid_layout.setContentsMargins(*([GRID_LAYOUT_CONTENT_MARGIN] * 4))
