# -*- coding: utf-8 -*-
import os
from pkm import ROOT, utils
from pkm.datastore import DataStore
from pkm.qtemplate import QTemplateWidget


class SettingsWidget(QTemplateWidget):
    TMPL = os.path.normpath(f'{ROOT}/pkm/tmpl/generalsettings.tmpl')

    def __init__(self, app, *args, **kwargs):
        super(SettingsWidget, self).__init__(*args, **kwargs)
        self.app = app
        self._init_data()
    
    def _init_data(self):
        monitors = []
        for i, screen in enumerate(self.app.screens()):
            monitor = utils.Bunch()
            monitor.value = i
            monitor.text = f'#{i} ({screen.name()})'
            monitors.append(monitor)
        self.data.update('generalsettings.monitors', monitors)
    
    # @QtCore.Property(type=list)
    # def position_choices(self):
    #     return ['Left', 'Right']
