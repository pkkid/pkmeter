# -*- coding: utf-8 -*-
"""
PKMeter About
"""
import os
from pkm import SHAREDIR, VERSION
from pkm.pkwidgets import PKWidget
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QT_VERSION_STR, PYQT_VERSION_STR
from xml.etree import ElementTree


class AboutWindow(PKWidget):
    TEMPLATE = os.path.join(SHAREDIR, 'templates', 'about.html')

    def __init__(self, parent=None):
        with open(self.TEMPLATE) as tmpl:
            template = ElementTree.fromstring(tmpl.read())
        PKWidget.__init__(self, template, self, parent)
        self.setWindowTitle('About PKMeter')
        self.setWindowFlags(Qt.Dialog)
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowIcon(QtGui.QIcon(QtGui.QPixmap('img:logo.png')))
        self.layout().setContentsMargins(0,0,0,0)
        self.layout().setSpacing(0)
        self._init_stylesheet()
        self.manifest.version.setText('Version %s' % VERSION)
        self.manifest.qt.setText('QT v%s, PyQT v%s' % (QT_VERSION_STR, PYQT_VERSION_STR))

    def _init_stylesheet(self):
        stylepath = os.path.join(SHAREDIR, 'pkmeter.css')
        with open(stylepath) as handle:
            self.setStyleSheet(handle.read())
