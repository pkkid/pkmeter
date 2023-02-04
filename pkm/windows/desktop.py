# -*- coding: utf-8 -*-
from os.path import dirname, join
from pkm import log
from pkm.qtemplate import QTemplateWidget
from PySide6.QtCore import Qt


class DesktopWindow(QTemplateWidget):
    TMPL = join(dirname(__file__), 'desktop.tmpl')
    DEFAULT_LAYOUT_MARGINS = (0,0,0,0)
    DEFAULT_LAYOUT_SPACING = 0

    def __init__(self, app):
        super(DesktopWindow, self).__init__()
        self.app = app
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self._init_toolbar_animation()
    
    def _init_toolbar_animation(self):
        policy = self.ids.toolbar.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        self.ids.toolbar.setSizePolicy(policy)
        self.ids.toolbar.hide()
    
    def enterEvent(self, event):
        self.ids.toolbar.show()

    def leaveEvent(self, event):
        self.ids.toolbar.hide()

    def show_settings(self):
        self.app.settings.show()
    
    def quit_app(self):
        self.app.quit()

    def mybutton_clicked(self):
        log.info('CLICK!')
