# -*- coding: utf-8 -*-
from pkm import log
from pkm.mixins import Draggable
from pkm.qtemplate import QTemplateWidget
from PySide6 import QtGui, QtCore
from PySide6.QtCore import Qt


class DeskWidget(Draggable, QTemplateWidget):
    DEFAULT_LAYOUT_MARGINS = (30,30,30,30)
    DEFAULT_LAYOUT_SPACING = 0

    def __init__(self, plugin):
        QTemplateWidget.__init__(self)
        Draggable.__init__(self)
        self.plugin = plugin
        self.app = QtCore.QCoreApplication.instance()
        self.setProperty('class', 'widget')
        self.setProperty('theme', self.plugin.themevar)
        self.setProperty('name', self.plugin.namevar)
        self.setObjectName(self.plugin.id)
        self._initWidget()
        self._initRightclickMenu()

    def _initWidget(self):
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        # Set the position
        pos = [int(x) for x in self.plugin.getValue('pos', '0,0').split(',')]
        self.move(pos[0], pos[1])
    
    def _initRightclickMenu(self):
        self.addAction(QtGui.QAction('Preferences', self, triggered=self.app.settings.show))
        self.addAction(QtGui.QAction('Quit', self, triggered=self.app.quit))
        self.setContextMenuPolicy(Qt.ActionsContextMenu)
    
    def show_settings(self):
        self.app.settings.show()
    
    def widgetMoved(self, pos):
        log.info(f'Widget Moved: {pos=}')
        self.plugin.saveValue('pos', f'{pos.x()},{pos.y()}')
