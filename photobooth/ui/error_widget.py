from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QLabel


class ErrorWidget(QLabel):
    accept = pyqtSignal()

    def set_message(self, message: str):
        self.setText(message)
