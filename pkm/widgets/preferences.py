# -*- coding: utf-8 -*-
import os
from pkm import ROOT
from pkm.qtemplate import QTemplateWidget


class SettingsWidget(QTemplateWidget):
    TMPL = os.path.normpath(f'{ROOT}/pkm/tmpl/preferences.tmpl')

    def __init__(self, app, *args, **kwargs):
        super(SettingsWidget, self).__init__(*args, **kwargs)
        self.app = app
