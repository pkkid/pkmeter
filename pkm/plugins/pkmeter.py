# -*- coding: utf-8 -*-
"""
Ping
Workaround for crashing QT5
"""
from pkm.plugin import BasePlugin

NAME = 'PKMeter'


class Plugin(BasePlugin):
    DEFAULT_INTERVAL = 60

    # @threaded_method
    # def enable(self):
    #     self.enabled = True
    #     return True

    # @never_raise
    # def update(self):
    #     with open(PINGFILE, 'a'):
    #         now = time.time()
    #         os.utime(PINGFILE, (now,now))
    #     super(Plugin, self).update()
