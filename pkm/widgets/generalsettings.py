# -*- coding: utf-8 -*-
import os
from pkm import ROOT, utils, log
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
    
    def setValue(self, key, value):
        """ Save a settigns value. """
        log.info(f'Saving generalsettings/{key} = {value}')
        # self.app.settings.storage.setValue(f'generalsettings/{key}', value)

    def setMonitor(self, index):
        """ Save new monitor value. """
        self.setValue('monitor', 'Hi Mom!')

    def setPosition(self, index):
        """ Save the new position value. """
        self.setValue('position', 'Hi Dad!')
