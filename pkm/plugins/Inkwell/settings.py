# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm import base, log, utils  # noqa


class SettingsWidget(base.SettingsWidget):
    TMPL = normpath(f'{dirname(__file__)}/settings.tmpl')

    def widthChanged(self, value):
        """ Save new monitor value. """
        self.component.saveSetting('width', value)
