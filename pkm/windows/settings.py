# -*- coding: utf-8 -*-
from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from pkm import STYLES


class SettingsWindow(QtWidgets.QWidget):

    def __init__(self, pkmeter):
        QtWidgets.QWidget.__init__(self)
        self.pkmeter = pkmeter
        self.setWindowTitle('PKMeter Settings')
        self.setLayout(QtWidgets.QVBoxLayout())
        self.setStyleSheet(STYLES)
        self.setWindowFlags(Qt.Tool)
