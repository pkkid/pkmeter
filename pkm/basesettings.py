# -*- coding: utf-8 -*-
from pkm.qtemplate import QTemplateWidget


class BaseSettings(QTemplateWidget):
    
    def __init__(self, component):
        super(BaseSettings, self).__init__()
        self.plugin = component.plugin
        self.component = component
