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
                disk = self._disk(disk)
                disk.update(self._disk_usage(disk['mountpoint']))
                disks.append(disk)
        self.data['disks'] = sorted(disks, key=lambda d:d['mountpoint'].lower())
        self.data['io'] = self._deltas(self.data.get('io',{}), self._disk_io_counters())
        super(Plugin, self).update()

    def _interesting(self, fstype):
        for fs in self.fstypes:
            if fstype.startswith(fs):
                return True
        return False

    def _disk(self, disk):
        return {
            'device': disk.device,
            'mountpoint': disk.mountpoint,
            'fstype': disk.fstype,
            'opts': disk.opts,
        }

    def _disk_usage(self, mountpoint):
        usage = psutil.disk_usage(mountpoint)
        return {
            'total': usage.total,
            'used': usage.used,
            'free': usage.free,
            'percent': usage.percent,
            'percent_free': 100 - usage.percent,
        }

    def _disk_io_counters(self):
        io = psutil.disk_io_counters()
        return {
            'read_count': io.read_count,
            'write_count': io.write_count,
            'read_bytes': io.read_bytes,
            'write_bytes': io.write_bytes,
            'read_time': io.read_time,
            'write_time': io.write_time,
        }

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
