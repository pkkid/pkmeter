# -*- coding: utf-8 -*-
"""
Processes Plugin
List Top Processes
"""
import psutil, shlex
from pkm import log
from pkm.decorators import never_raise, threaded_method
from pkm.plugin import BasePlugin, BaseConfig
from subprocess import Popen, DEVNULL

NAME = 'Processes'


class Plugin(BasePlugin):
    DEFAULT_INTERVAL = 3

    @threaded_method
    def enable(self):
        self.procs = {}
        self.sortkey = 'cpu_percent'
        super(Plugin, self).enable()

    @never_raise
    def update(self):
        pids = set()
        for pid in list(psutil.pids()):
            try:
                proc = self.procs.get(pid, {}).get('proc')
                if not proc:
                    proc = psutil.Process(pid)
                    self.procs[pid] = {
                        'proc': proc,
                        'pid': pid,
                        'cmdline': proc.cmdline(),
                        'create_time': proc.create_time(),
                        'name': proc.name(),
                        'username': proc.username(),
                    }
                self.procs[pid]['cpu_percent'] = proc.cpu_percent()
                self.procs[pid]['memory_rss'] = proc.memory_info().rss
                self.procs[pid]['status'] = proc.status()
                pids.add(pid)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        for pid in [p for p in self.procs if p not in pids]:
            del self.procs[pid]
        self.data['sort'] = self.sortkey
        self.data['total'] = len(self.procs)
        self.data['procs'] = sorted(self.procs.values(), key=lambda p: p[self.sortkey], reverse=True)
        super(Plugin, self).update()

    def sort_cpu(self):
        self.sortkey = 'cpu_percent'
        self.update()

    def sort_mem(self):
        self.sortkey = 'memory_rss'
        self.update()

    @never_raise
    def open_system_monitor(self, widget):
        cmd = '/usr/bin/gnome-system-monitor -p'
        log.info('Opening system monitor: %s', cmd)
        Popen(shlex.split(cmd), stdout=DEVNULL, stderr=DEVNULL)


class Config(BaseConfig):
    pass
