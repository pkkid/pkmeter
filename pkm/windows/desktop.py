# -*- coding: utf-8 -*-
from PySide2 import QtWidgets
from PySide2.QtCore import Qt
from pkm import STYLES


class DesktopWindow(QtWidgets.QWidget):

    def __init__(self, pkmeter):
        QtWidgets.QWidget.__init__(self)
        self.pkmeter = pkmeter
        self.setLayout(QtWidgets.QVBoxLayout())
        self.setStyleSheet(STYLES)
        # self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.Tool |
            Qt.FramelessWindowHint |
            # Qt.WindowStaysOnBottomHint |
            Qt.NoDropShadowWindowHint |
            Qt.CustomizeWindowHint)
        self.layout().setContentsMargins(20,40,20,40)
        self.layout().setSpacing(0)
        self._init_menu()
        self.show()
    
    def _init_menu(self):
        # self.addAction(QtWidgets.QAction('About PKMeter', self, triggered=self.pkmeter.about.show))
        self.addAction(QtWidgets.QAction('Settings', self, triggered=self.pkmeter.windows.settings.show))
        self.addAction(QtWidgets.QAction('Quit', self, triggered=self.pkmeter.quit))
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
