# -*- coding: utf-8 -*-
from pkm.qtemplate import QTemplateWidget
from PySide6 import QtGui, QtCore
from PySide6.QtCore import Qt


class DeskWidget(QTemplateWidget):
    DEFAULT_LAYOUT_MARGINS = (0,0,0,0)
    DEFAULT_LAYOUT_SPACING = 0

    def __init__(self, plugin):
        super(DeskWidget, self).__init__()
        self.app = QtCore.QCoreApplication.instance()
        self.plugin = plugin
        self.mousepos = None
        self.widgetpos = None
        self._initWidget()
        self._initRightclickMenu()

    def _initWidget(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setGeometry(10, 10, 200, 100)
    
    def _initRightclickMenu(self):
        self.addAction(QtGui.QAction('Preferences', self, triggered=self.app.settings.show))
        self.addAction(QtGui.QAction('Quit', self, triggered=self.app.quit))
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

    def mousePressEvent(self, event):
        self.mousepos = event.globalPos()
        self.widgetpos = self.pos()

    def mouseMoveEvent(self, event):
        if self.mousepos:
            delta = event.globalPos() - self.mousepos
            self.move(self.widgetpos + delta)

    def mouseReleaseEvent(self, event):
        self.mousepos = None
        self.widgetpos = None
    
    def show_settings(self):
        self.app.settings.show()
