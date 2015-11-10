# -*- coding: utf-8 -*-
"""
Network Plugin
Network usage and connections
"""
import os, netifaces, psutil, time
from pkm import utils, SHAREDIR
from pkm.decorators import never_raise, threaded_method
from pkm.plugin import BasePlugin, BaseConfig
from pkm.filters import register_filter

NAME = 'Network'
DEFAULT_IGNORES = 'lxc tun'


class Plugin(BasePlugin):
    DEFAULT_INTERVAL = 1

    @threaded_method
    def enable(self):
        self.nics = {}
        self.ignores = self.pkmeter.config.get(self.namespace, 'ignores', '')
        self.ignores = list(filter(None, self.ignores.split(' ')))
        super(Plugin, self).enable()

    @never_raise
    def update(self):
        for iface, newio in psutil.net_io_counters(True).items():
            if not iface.startswith('lo'):
                netinfo = netifaces.ifaddresses(iface)
                if netinfo.get(netifaces.AF_INET) and not self._is_ignored(iface):
                    newio = self._net_io_counters(newio)
                    newio['iface'] = iface
                    newio.update(netinfo[netifaces.AF_INET][0])
                    self._deltas(self.nics.get(iface,{}), newio)
                    self.nics[iface] = newio
                elif iface in self.nics:
                    del self.nics[iface]
        self.data['nics'] = sorted(self.nics.values(), key=lambda n:n['iface'])
        self.data['total'] = self._deltas(self.data.get('total',{}), self._net_io_counters())
        super(Plugin, self).update()

    def _is_ignored(self, iface):
        if self.ignores:
            for ignore in self.ignores:
                if iface.startswith(ignore):
                    return True
        return False

    def _net_io_counters(self, io=None):
        io = io or psutil.net_io_counters()
        return {
            'bytes_sent': io.bytes_sent,
            'bytes_recv': io.bytes_recv,
            'packets_sent': io.packets_sent,
            'packets_recv': io.packets_recv,
            'errin': io.errin,
            'errout': io.errout,
            'dropin': io.dropin,
            'dropout': io.dropout,
        }

    def _deltas(self, previo, newio):
        now = time.time()
        tdelta = now - previo.get('updated',0)
        for key in ['bytes_sent', 'bytes_recv']:
            newio['%s_per_sec' % key] = int((newio[key] - previo.get(key,0)) / tdelta)
        newio['updated'] = now
        return newio


class Config(BaseConfig):
    TEMPLATE = os.path.join(SHAREDIR, 'templates', 'network_config.html')
    FIELDS = utils.Bunch(BaseConfig.FIELDS,
        ignores = {'default':DEFAULT_IGNORES}
    )


@register_filter()
def network_friendly_iface(iface):
    iface = iface.replace('eth', 'Ethernet ')
    iface = iface.replace('wlan', 'Wireless ')
    iface = iface.replace(' 0', '')
    return iface
