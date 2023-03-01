# -*- coding: utf-8 -*-
from os.path import dirname, normpath
from pkm import log, utils  # noqa
from pkm.qtemplate import QTemplateWidget


class SettingsWidget(QTemplateWidget):
    TMPL = normpath(f'{dirname(__file__)}/settings.tmpl')

    def __init__(self, component, *args, **kwargs):
        super(SettingsWidget, self).__init__(*args, **kwargs)
        self.plugin = component.plugin
        self.component = component

    def widthChanged(self, value):
        """ Save new monitor value. """
        self.plugin.saveSetting('width', value)
