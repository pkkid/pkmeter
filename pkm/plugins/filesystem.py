# -*- coding: utf-8 -*-
"""
FileSystem Plugin
FileSystem usage
"""
import os, psutil, time
from pkm import utils, SHAREDIR
from pkm.decorators import never_raise, threaded_method
from pkm.plugin import BasePlugin, BaseConfig
from pkm.filters import register_filter

NAME = 'File System'
DEFAULT_FSTYPES = 'cifs ext nfs vfat'


class Plugin(BasePlugin):
    DEFAULT_INTERVAL = 5

    @threaded_method
    def enable(self):
        self.fstypes = self.pkmeter.config.get(self.namespace, 'fstypes', '')
        self.fstypes = list(filter(None, self.fstypes.split(' ')))
        super(Plugin, self).enable()

    @never_raise
    def update(self):
        disks = []
        for disk in psutil.disk_partitions(all=True):
            if self._interesting(disk.fstype):
                disk = disk.__dict__
                disk.update(psutil.disk_usage(disk['mountpoint']).__dict__)
                disk['percent_free'] = 100 - disk['percent']
                disks.append(disk)
        self.data['disks'] = sorted(disks, key=lambda d:d['mountpoint'].lower())
        self.data['io'] = self._deltas(self.data.get('io',{}), psutil.disk_io_counters().__dict__)
        super(Plugin, self).update()

    def _interesting(self, fstype):
        for fs in self.fstypes:
            if fstype.startswith(fs):
                return True
        return False

    def _deltas(self, previo, newrw):
        now = time.time()
        tdelta = now - previo.get('updated',0)
        for key in ['read_bytes', 'write_bytes']:
            newrw['%s_per_sec' % key] = int((newrw[key] - previo.get(key,0)) / tdelta)
        newrw['io_per_sec'] = newrw.get('read_bytes_per_sec',0) + newrw.get('write_bytes_per_sec',0)
        newrw['updated'] = now
        return newrw


class Config(BaseConfig):
    TEMPLATE = os.path.join(SHAREDIR, 'templates', 'filesystem_config.html')
    FIELDS = utils.Bunch(BaseConfig.FIELDS,
        fstypes = {'default': DEFAULT_FSTYPES}
    )


@register_filter()
def filesystem_friendly_name(mountpoint):
    name = os.path.basename(mountpoint)
    name = 'Root' if not name else name
    return name
