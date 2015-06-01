# -*- coding: utf-8 -*-
"""
System Plugin
General System and Memory usage
"""
import psutil, socket, shlex, time
from pkm import log
from pkm.decorators import never_raise, threaded_method
from pkm.plugin import BasePlugin, BaseConfig
from subprocess import Popen, DEVNULL

NAME = 'System'


class Plugin(BasePlugin):
    DEFAULT_INTERVAL = 1

    @threaded_method
    def enable(self):
        self.data['cpu_count'] = psutil.cpu_count()
        self.data['hostname'] = socket.gethostname()
        self.data['boot_time'] = psutil.boot_time()
        super(Plugin, self).enable()

    @never_raise
    def update(self):
        self.data['cpu_percent'] = psutil.cpu_percent()
        self.data['cpu_percents'] = psutil.cpu_percent(percpu=True)
        self.data['memory'] = psutil.virtual_memory().__dict__
        self.data['memory']['cached_percent'] = round((self.data['memory']['cached'] / self.data['memory']['total']) * 100, 1)
        self.data['swap'] = psutil.swap_memory().__dict__
        self.data['uptime'] = int(time.time() - self.data['boot_time'])
        super(Plugin, self).update()

    @never_raise
    def open_system_monitor(self, widget):
        cmd = '/usr/bin/gnome-system-monitor -r'
        log.info('Opening system monitor: %s', cmd)
        Popen(shlex.split(cmd), stdout=DEVNULL, stderr=DEVNULL)


class Config(BaseConfig):
    pass
