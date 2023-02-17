# -*- coding: utf-8 -*-
import os
from pkm import ROOT, utils, log
from pkm.qtemplate import QTemplateWidget
from PySide6.QtCore import QCoreApplication


class SettingsWidget(QTemplateWidget):
    TMPL = os.path.normpath(f'{ROOT}/pkm/tmpl/gensettings.tmpl')

    def __init__(self, *args, **kwargs):
        super(SettingsWidget, self).__init__(*args, **kwargs)
    
    def _initData(self):
        monitors = []
        app = QCoreApplication.instance()
        for i, screen in enumerate(app.screens()):
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
