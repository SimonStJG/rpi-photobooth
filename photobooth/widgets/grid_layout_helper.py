from PyQt5.QtWidgets import QGridLayout

GRID_LAYOUT_CONTENT_MARGIN = 100


# TODO Work out how to set this with qss
def set_grid_content_margins(grid_layout: QGridLayout):
    grid_layout.setContentsMargins(*([GRID_LAYOUT_CONTENT_MARGIN] * 4))
