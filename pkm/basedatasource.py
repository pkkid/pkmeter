# -*- coding: utf-8 -*-
from pkm.qtemplate import QTemplateWidget


class BaseDataSource(QTemplateWidget):
    
    def __init__(self, plugin):
        super(BaseDataSource, self).__init__()
        self.plugin = plugin
