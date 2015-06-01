# -*- coding: utf-8 -*-
"""
Ping
Workaround for crashing QT5
"""
import os, time
from pkm import CONFIGDIR
from pkm.decorators import never_raise, threaded_method
from pkm.plugin import BasePlugin

NAME = 'Ping'
PINGFILE = os.path.join(CONFIGDIR, 'ping')


class Plugin(BasePlugin):
    DEFAULT_INTERVAL = 30

    @threaded_method
    def enable(self):
        self.enabled = True
        return True

    @never_raise
    def update(self):
        with open(PINGFILE, 'a'):
            now = time.time()
            os.utime(PINGFILE, (now,now))
        super(Plugin, self).update()
