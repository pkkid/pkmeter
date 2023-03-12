# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm import base, log, utils  # noqa


class SettingsWidget(base.SettingsWidget):
    TMPL = normpath(f'{dirname(__file__)}/settings.tmpl')

    def initSettings(self):
        """ Set all values in the settings Widget. """
        self.ids.width.setValue(self.getValue('width', 180))
        self.ids.borderRadius.setValue(self.getValue('borderRadius', 5))
        self.ids.backgroundColor.setColor(self.getValue('backgroundColor', '#000000'))

    def widthChanged(self, value):
        """ Save new widget width. """
        self.saveSetting('width', value)
    
    def backgroundColorChanged(self, value):
        """ Save new backgroundColor value. """
        self.saveSetting('backgroundColor', value)
        
    def borderRadiusChanged(self, value):
        """ Save new borderRadius value. """
        self.saveSetting('borderRadius', value)
