# -*- coding: utf-8 -*-
from pkm.qtemplate import QTemplateWidget


class BaseSettings(QTemplateWidget):
    
    def __init__(self, plugin):
        super(BaseSettings, self).__init__()
        self.plugin = plugin
