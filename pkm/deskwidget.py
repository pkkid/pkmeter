# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm.qtemplate import QTemplateWidget
from PySide6 import QtGui
from PySide6.QtCore import Qt


class DeskWidget(QTemplateWidget):
    # TMPL = normpath(f'{dirname(__file__)}/tmpl/desktop.tmpl')
    DEFAULT_LAYOUT_MARGINS = (0,0,0,0)
    DEFAULT_LAYOUT_SPACING = 0

    def __init__(self, plugin):
        super(DeskWidget, self).__init__()
        self.plugin = plugin
        # self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        # self._initRightclickMenu()
    
    def _initRightclickMenu(self):
        self.addAction(QtGui.QAction('Preferences', self, triggered=self.app.settings.show))
        self.addAction(QtGui.QAction('Quit', self, triggered=self.app.quit))
        self.setContextMenuPolicy(Qt.ActionsContextMenu)

    def show_settings(self):
        self.app.settings.show()
    
    def quit_app(self):
        self.app.quit()
