# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm import base, log, utils  # noqa


class SettingsWidget(base.SettingsWidget):
    TMPL = normpath(f'{dirname(__file__)}/settings.tmpl')

    def initSettings(self):
        """ Set all values in the settings Widget. """
        self.ids.width.setValue(self.component.getValue('width', 180))
        self.ids.borderRadius.setValue(self.component.getValue('borderRadius', 5))

    def widthChanged(self, value):
        """ Save new monitor value. """
        self.component.saveSetting('width', value)
    
    def borderRadiusChanged(self, value):
        """ Save new border-radius value. """
        self.component.saveSetting('borderRadius', value)
