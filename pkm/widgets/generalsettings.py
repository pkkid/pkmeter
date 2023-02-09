# -*- coding: utf-8 -*-
import os
from pkm import ROOT
from pkm.qtemplate import QTemplateWidget
from PySide6 import QtCore


class SettingsWidget(QTemplateWidget):
    TMPL = os.path.normpath(f'{ROOT}/pkm/tmpl/generalsettings.tmpl')

    def __init__(self, app, *args, **kwargs):
        super(SettingsWidget, self).__init__(*args, **kwargs)
        self.app = app
    
    @QtCore.Property(type=list)
    def monitor_choices(self):
        choices = []
        for i, screen in enumerate(self.parent.app.screens()):
            choices.append({'value':0, 'text':f'#{i} ({screen.name()})'})
        return choices
    
    @QtCore.Property(type=list)
    def position_choices(self):
        return ['Left', 'Right']
