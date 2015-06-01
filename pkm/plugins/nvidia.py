# -*- coding: utf-8 -*-
"""
Sensors Plugin
"""
from pkm import log, utils
from pkm.decorators import never_raise, threaded_method
from pkm.plugin import BasePlugin, BaseConfig

NAME = 'NVIDIA'
NVIDIA_SETTINGS = '/usr/bin/nvidia-settings'
NVIDIA_ATTRS = ('nvidiadriverversion', 'gpucoretemp', 'gpuambienttemp', 'gpucurrentfanspeedrpm',
    'gpuutilization', 'totaldedicatedgpumemory', 'useddedicatedgpumemory')
NVIDIA_QUERY = '%s --query=%s' % (NVIDIA_SETTINGS, ' --query='.join(NVIDIA_ATTRS))


class Plugin(BasePlugin):
    DEFAULT_INTERVAL = 2

    @threaded_method
    def enable(self):
        try:
            self.card_name = self._fetch_card_name()
            result = utils.get_stdout('%s --version' % NVIDIA_SETTINGS)
            assert 'NVIDIA' in result, 'nvidia-settings not found.'
            super(Plugin, self).enable()
        except Exception as err:
            log.warning('NVIDIA plugin disabled: %s', err)
            return self.disable()

    @never_raise
    def update(self):
        self.data['card'] = self.card_name or 'Unknown'
        output = utils.get_stdout(NVIDIA_QUERY)
        for attr, value in self._parse_attributes(output):
            self.data[attr] = value
        # Calculate used and percent memory
        mem_total = utils.to_int(self.data['totaldedicatedgpumemory'], 0)
        mem_used = utils.to_int(self.data['useddedicatedgpumemory'], 0)
        self.data['freededicatedgpumemory'] = mem_total - mem_used
        self.data['percentuseddedicatedgpumemory'] = utils.percent(mem_used, mem_total, 0)
        super(Plugin, self).update()

    def _parse_attributes(self, output):
        for line in output.split('\n'):
            line = line.lower().strip(' .').replace("'", '')
            for attr in NVIDIA_ATTRS:
                if line.startswith('attribute %s ' % attr) and ('gpu:0' in line or 'fan:0' in line):
                    value = line.split(':')[-1].strip()
                    if attr in ['gpuutilization']:
                        for key, subval in self._parse_multivalue_attribute(value):
                            subattr = '%s_%s' % (attr, key)
                            yield subattr, subval
                    else:
                        yield attr, value

    def _parse_multivalue_attribute(self, value):
        for subpart in value.strip(' ,').split(','):
            subkey, subvalue = subpart.split('=')
            yield subkey, int(subvalue)

    @never_raise
    def _fetch_card_name(self):
        for line in utils.get_stdout('%s --glxinfo' % NVIDIA_SETTINGS).split('\n'):
            if line.strip().lower().startswith('opengl renderer string:'):
                return line.split(':', 1)[1].split('/')[0].strip()


class Config(BaseConfig):
    pass
