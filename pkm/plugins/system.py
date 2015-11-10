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
        self.data['memory'] = self._virtual_memory()
        self.data['swap'] = self._swap_memory()
        self.data['uptime'] = int(time.time() - self.data['boot_time'])
        super(Plugin, self).update()

    def _virtual_memory(self):
        vmem = psutil.virtual_memory()
        return {
            'total': vmem.total,
            'available': vmem.available,
            'percent': vmem.percent,
            'used': vmem.used,
            'free': vmem.free,
            'active': vmem.active,
            'inactive': vmem.inactive,
            'buffers': vmem.buffers,
            'cached': vmem.cached,
            'cached_percent': round((vmem.cached / vmem.total) * 100, 1)
        }

    def _swap_memory(self):
        swap = psutil.swap_memory()
        return {
            'total': swap.total,
            'used': swap.used,
            'free': swap.free,
            'percent': swap.percent,
            'sin': swap.sin,
            'sout': swap.sout,
        }

    @never_raise
    def open_system_monitor(self, widget):
        cmd = '/usr/bin/gnome-system-monitor -r'
        log.info('Opening system monitor: %s', cmd)
        Popen(shlex.split(cmd), stdout=DEVNULL, stderr=DEVNULL)


class Config(BaseConfig):
    pass
