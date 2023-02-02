#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pkm import ROOT, log
from pkm.qtemplate import QTemplateWidget
from PySide6.QtCore import Qt


class DesktopWindow(QTemplateWidget):
    TMPL = os.path.join(ROOT, 'tmpl', 'desktop.tmpl')

    def __init__(self):
        log.info(f'Creating {self.__class__.__name__}')
        super(DesktopWindow, self).__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
    
    def mybutton_clicked(self):
        log.info('CLICK!')
