# -*- coding: utf-8 -*-
"""
Clock Plugin
Provides the datetime
"""
import datetime
from pkm.decorators import never_raise
from pkm.plugin import BasePlugin, BaseConfig

NAME = 'Clock'


class Plugin(BasePlugin):
    DEFAULT_INTERVAL = 1

    @never_raise
    def update(self):
        self.data['datetime'] = datetime.datetime.now()
        super(Plugin, self).update()


class Config(BaseConfig):
    pass
