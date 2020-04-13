from dataclasses import dataclass

from PyQt5.QtGui import QImage


class Idle:
    pass


@dataclass
class Preview:
    image: QImage


@dataclass
class Printing:
    image: QImage
